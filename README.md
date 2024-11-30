# AI Code Review Integration with Jira Cloud

This application integrates AI-powered code review capabilities with Jira Cloud. It automatically processes code changes associated with Jira issues and provides AI-generated code reviews as comments.

## Features

- Integration with Jira Cloud
- AI-powered code review using configurable AI services
- Automated comment creation with review results
- Git integration for code change analysis
- FastAPI with automatic OpenAPI documentation
- Health monitoring endpoints
- Graceful error handling
- Automated code formatting and linting with pre-commit hooks

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Git (for version control and pre-commit hooks)
- Jira Cloud account
- AI service API access (korbit.ai or codeant.ai)

## Setup

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

5. **Configure Jira Cloud**:
   - Sign up for [Jira Cloud](https://www.atlassian.com/software/jira/free)
   - Create a new project (e.g., with key "AIREV")
   - Generate an API token:
     1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security)
     2. Create an API token
     3. Save the token securely

6. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # - JIRA_URL=your-domain.atlassian.net
   # - JIRA_USERNAME=your-email@domain.com
   # - JIRA_API_TOKEN=your-generated-token
   # - JIRA_PROJECT_KEY=AIREV
   ```

7. **Run the application**:
   ```bash
   poetry run uvicorn app:app --reload
   ```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "jira_connection": true,
  "ai_service_connection": true
}
```

### Trigger Code Review
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "issue_key": "AIREV-123",
    "branch_name": "feature/new-feature"
  }'
```

## Documentation

- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc
- Architecture documentation: [docs/architecture.md](docs/architecture.md)

## Configuration

Configure the application using the following environment variables:

- `JIRA_URL`: Your Jira Cloud domain (e.g., your-domain.atlassian.net)
- `JIRA_USERNAME`: Your Jira Cloud email
- `JIRA_API_TOKEN`: Your Jira API token
- `JIRA_PROJECT_KEY`: Your Jira project key (default: AIREV)
- `REPO_PATH`: Path to your Git repository
- `AI_SERVICE_URL`: URL of the AI service API
- `AI_SERVICE_API_KEY`: API key for the AI service
- `DEBUG`: Enable debug mode (default: false)

## Development

1. **Code Style**:
   ```bash
   # Format code
   poetry run black .
   poetry run isort .

   # Check style
   poetry run flake8
   ```

2. **Pre-commit Hooks**:
   - Automatically run on `git commit`
   - Run manually: `poetry run pre-commit run --all-files`
   - Skip: `git commit -m "message" --no-verify`

## Project Structure

```
.
├── app.py               # FastAPI application
├── config.py            # Configuration management
├── services/           # Service modules
│   ├── ai_review_service.py  # AI review integration
│   ├── git_service.py        # Git operations
│   └── jira_service.py       # Jira Cloud integration
└── docs/               # Documentation
    └── architecture.md  # Technical architecture
```

## Troubleshooting

1. **Jira Connection Issues**:
   - Verify your Jira Cloud URL format
   - Check API token permissions
   - Ensure email matches Jira account

2. **Git Integration Issues**:
   - Verify repository path
   - Check branch exists
   - Ensure Git is installed

3. **AI Service Issues**:
   - Verify API credentials
   - Check service status
   - Review request format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `poetry install`
4. Set up pre-commit hooks: `poetry run pre-commit install`
5. Ensure code passes all checks:
   ```bash
   poetry run pre-commit run --all-files
   ```
6. Create a Pull Request

## License

[Your chosen license]