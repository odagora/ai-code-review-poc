from typing import Dict, Any
from jira import JIRA
import time
from functools import lru_cache
from config import Settings


class JiraService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None
        self._max_retries = 5
        self._retry_delay = 10  # seconds

    @property
    def client(self) -> JIRA:
        """Lazy initialization of JIRA client with retry logic"""
        if self._client is None:
            for attempt in range(self._max_retries):
                try:
                    self._client = JIRA(
                        server=self.settings.get_jira_cloud_url(),
                        basic_auth=(
                            self.settings.JIRA_USERNAME,
                            self.settings.JIRA_API_TOKEN,
                        ),
                    )
                    # Test the connection
                    self._client.server_info()
                    break
                except Exception as e:
                    if attempt == self._max_retries - 1:
                        raise Exception(
                            f"Failed to connect to Jira after {self._max_retries} attempts: {str(e)}"
                        )
                    print(
                        f"Attempt {attempt + 1} failed, retrying in {self._retry_delay} seconds..."
                    )
                    time.sleep(self._retry_delay)
        return self._client

    def get_issue_context(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue context for code review

        Args:
            issue_key: The Jira issue key (e.g., AIREV-123)

        Returns:
            Dictionary containing issue context
        """
        # Verify the issue exists and belongs to our project
        issue = self.client.issue(issue_key)
        if not issue.fields.project.key == self.settings.JIRA_PROJECT_KEY:
            raise ValueError(
                f"Issue {issue_key} does not belong to project {self.settings.JIRA_PROJECT_KEY}"
            )

        return {
            "issue_key": issue_key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "issue_type": issue.fields.issuetype.name,
            "status": issue.fields.status.name,
            "assignee": (
                issue.fields.assignee.displayName if issue.fields.assignee else None
            ),
        }

    def update_with_review(
        self, issue_key: str, review_results: Dict[str, Any]
    ) -> None:
        """
        Update Jira issue with AI review results

        Args:
            issue_key: The Jira issue key
            review_results: The AI review results to add as a comment
        """
        issue = self.client.issue(issue_key)

        # Create a comment with the review results
        comment_body = self._format_review_comment(review_results)
        self.client.add_comment(issue, comment_body)

        # Update issue status if configured
        if review_results.get("status") == "failed":
            self._transition_issue(issue, "Review Failed")
        elif review_results.get("status") == "success":
            self._transition_issue(issue, "Review Passed")

    def _transition_issue(self, issue: JIRA.Issue, status_name: str) -> None:
        """
        Transition issue to a new status if the transition is available

        Args:
            issue: The Jira issue to transition
            status_name: The name of the status to transition to
        """
        transitions = self.client.transitions(issue)
        for t in transitions:
            if t["name"].lower() == status_name.lower():
                self.client.transition_issue(issue, t["id"])
                break

    def _format_review_comment(self, review_results: Dict[str, Any]) -> str:
        """
        Format AI review results into a readable comment

        Args:
            review_results: The AI review results to format

        Returns:
            Formatted comment string
        """
        comment = "{panel:title=AI Code Review Results|borderStyle=solid|borderColor=#ccc|titleBGColor=#f0f0f0|bgColor=#fff}\n\n"

        if "summary" in review_results:
            comment += f"h3. Summary\n{review_results['summary']}\n\n"

        if "suggestions" in review_results:
            comment += "h3. Suggestions\n"
            for suggestion in review_results["suggestions"]:
                comment += f"* {suggestion}\n"

        comment += "\n{panel}"
        return comment

    @lru_cache(maxsize=1)
    def check_health(self) -> bool:
        """
        Check if Jira connection is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            self.client.server_info()
            return True
        except Exception:
            return False
