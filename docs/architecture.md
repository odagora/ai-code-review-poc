# AI Code Review Architecture

This document describes the architecture and flow of the AI Code Review system integrated with Jira Cloud.

## System Components

```mermaid
graph TB
    subgraph "External Services"
        JIRA[Jira Cloud]
        AI_API[AI Review API<br/>korbit.ai/codeant.ai]
    end

    subgraph "Local Environment"
        GIT[Git Repository]
    end

    subgraph "AI Code Review Service"
        API[FastAPI Service]
        JS[Jira Service]
        GS[Git Service]
        AIS[AI Service]
        CFG[Configuration]
    end

    API --> JS
    API --> GS
    API --> AIS
    JS --> JIRA
    GS --> GIT
    AIS --> AI_API
    CFG --> JS
    CFG --> AIS
```

## Review Process Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Service
    participant JS as Jira Service
    participant GS as Git Service
    participant JIRA as Jira Cloud
    participant GIT as Git Repository
    participant AIS as AI Service
    participant AI_API as AI Review API

    User->>API: POST /review<br/>{issue_key, branch_name}

    API->>JS: Verify issue exists
    JS->>JIRA: Get issue details
    JIRA-->>JS: Issue info

    API->>GS: Get code changes
    GS->>GIT: Fetch branch diff
    GIT-->>GS: Code changes
    GS-->>API: Formatted changes

    API->>AIS: Request code review
    AIS->>AI_API: Submit code for review
    AI_API-->>AIS: Review results

    API->>JS: Update issue
    JS->>JIRA: Add review comment
    JS->>JIRA: Update status

    API-->>User: Review results
```

## Service Architecture

### FastAPI Service
The main application service built with FastAPI provides:
- RESTful API endpoints
- Request validation using Pydantic models
- Automatic OpenAPI documentation
- Health monitoring
- Service coordination

### Jira Service
Handles all interactions with Jira Cloud:
- Issue verification and retrieval
- Comment management
- Status transitions
- Error handling and retries

### Git Service
Manages local Git operations:
- Branch diff retrieval
- Code change formatting
- Author tracking
- Change metadata collection

### AI Service
Coordinates with the AI review provider:
- Code review requests
- Response processing
- Error handling
- Result formatting

## Data Models

### Review Request
```python
class ReviewRequest(BaseModel):
    issue_key: str      # e.g., "AIREV-123"
    branch_name: str    # e.g., "feature/new-feature"
```

### Review Response
```python
class ReviewResponse(BaseModel):
    status: str         # "success" or "failed"
    issue_key: str      # The reviewed issue
    review_results: dict # Complete review details
```

### Code Changes
```python
CodeChange = Dict[str, Any]
{
    "file_path": str,   # Path to changed file
    "changes": str,     # Actual code changes
    "author": str,      # Change author
    "jira_context": {   # Additional context
        "issue_key": str,
        "issue_summary": str,
        "issue_type": str
    }
}
```

## Configuration Management

```mermaid
flowchart TD
    subgraph ENV[Environment Variables]
        E1[JIRA_URL]
        E2[JIRA_USERNAME]
        E3[JIRA_API_TOKEN]
        E4[JIRA_PROJECT_KEY]
        E5[REPO_PATH]
        E6[AI_SERVICE_URL]
        E7[AI_SERVICE_API_KEY]
    end

    subgraph CFG[Configuration]
        C1[Settings Class]
        C2[Validation]
        C3[URL Formatting]
    end

    subgraph SVC[Services]
        S1[Jira Service]
        S2[Git Service]
        S3[AI Service]
    end

    ENV --> CFG
    CFG --> SVC
```

## Error Handling

The system implements multiple layers of error handling:

1. **Request Validation**
   - Input validation using Pydantic
   - Project key verification
   - Branch existence checks

2. **Service Errors**
   - Jira connection retries
   - Git operation fallbacks
   - AI service timeouts

3. **Response Processing**
   - Result validation
   - Error formatting
   - Status tracking

## Security Considerations

1. **Authentication**
   - Jira Cloud API tokens
   - AI service API keys
   - No sensitive data in logs

2. **Data Protection**
   - Code changes processed locally
   - Minimal data sent to AI service
   - No storage of sensitive data

3. **Access Control**
   - Project-based access
   - Role-based permissions
   - Audit trail in Jira

## Deployment Considerations

1. **Dependencies**
   - Python 3.11+
   - Git installation
   - Network access to Jira Cloud
   - AI service connectivity

2. **Performance**
   - Async operations where possible
   - Connection pooling
   - Response caching
   - Timeout handling

3. **Monitoring**
   - Health endpoints
   - Service status
   - Error tracking
   - Performance metrics