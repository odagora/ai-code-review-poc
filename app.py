from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from services.jira_service import JiraService
from services.ai_review_service import AIReviewService
from services.git_service import GitService
from config import get_settings

app = FastAPI(
    title="AI Code Review Service",
    description="AI-powered code review integration with Jira",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize services
settings = get_settings()
git_service = GitService(settings.REPO_PATH)
jira_service = JiraService(settings)
ai_review_service = AIReviewService(settings)


class ReviewRequest(BaseModel):
    issue_key: str = Field(..., description="Jira issue key (e.g., AIREV-123)")
    branch_name: str = Field(..., description="Git branch name to review")

    class Config:
        schema_extra = {
            "example": {
                "issue_key": "AIREV-123",
                "branch_name": "feature/new-feature",
            }
        }


class ReviewResponse(BaseModel):
    status: str = Field(..., description="Status of the review request")
    issue_key: str = Field(..., description="Jira issue key that was reviewed")
    review_results: dict = Field(..., description="Complete review results")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service health status")
    jira_connection: bool = Field(..., description="Jira connection status")
    ai_service_connection: bool = Field(..., description="AI service connection status")
    git_connection: bool = Field(..., description="Git connection status")


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Perform a health check on the service.

    Returns:
        HealthResponse: Health status of all service components
    """
    jira_health = jira_service.check_health()
    git_health = git_service is not None
    # We'll assume AI service is healthy for now
    ai_health = True

    overall_status = (
        "healthy" if all([jira_health, git_health, ai_health]) else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        jira_connection=jira_health,
        git_connection=git_health,
        ai_service_connection=ai_health,
    )


@app.post(
    "/review",
    tags=["Code Review"],
    summary="Trigger Code Review",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Service temporarily unavailable"},
    },
)
async def review_code(request: ReviewRequest):
    """
    Trigger an AI-powered code review for a specific Jira issue.

    The review process includes:
    1. Fetching code changes from the specified branch
    2. Performing AI analysis on the changes
    3. Updating the Jira issue with review results

    Args:
        request (ReviewRequest): The review request containing Jira issue key and branch name

    Returns:
        ReviewResponse: The review results and status

    Raises:
        HTTPException: If there's an error during the review process
    """
    # Check service health before proceeding
    health = await health_check()
    if health.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not fully operational. Check /health endpoint for details.",
        )

    try:
        # Get code changes from Git
        code_changes = git_service.get_branch_changes(request.branch_name)

        # Add Jira context to changes
        jira_context = jira_service.get_issue_context(request.issue_key)
        for change in code_changes:
            change["jira_context"] = jira_context

        # Perform AI review
        review_results = ai_review_service.review_code(code_changes)

        # Update Jira with review results
        jira_service.update_with_review(request.issue_key, review_results)

        return ReviewResponse(
            status="success",
            issue_key=request.issue_key,
            review_results=review_results,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
