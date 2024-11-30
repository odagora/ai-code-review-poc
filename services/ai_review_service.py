from typing import Dict, List, Any
import requests
from config import Settings


class AIReviewService:
    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.AI_SERVICE_URL:
            print("Warning: AI_SERVICE_URL not configured")

    def review_code(self, code_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submit code changes for AI review

        Args:
            code_changes: List of code changes to review, each containing:
                - file_path: Path to the file
                - changes: The actual code changes
                - author: Author of the changes
                - jira_context: Additional Jira context

        Returns:
            Dictionary containing:
                - status: 'success' or 'failed'
                - summary: Overall review summary
                - suggestions: List of specific suggestions
                - error: Error message if status is 'failed'
        """
        if not self.settings.AI_SERVICE_URL or not self.settings.AI_SERVICE_API_KEY:
            return {
                "status": "failed",
                "error": "AI service not configured",
                "suggestions": [],
                "summary": "Unable to perform code review: AI service not configured",
            }

        headers = {
            "Authorization": f"Bearer {self.settings.AI_SERVICE_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            # Format the code changes according to the AI service's API requirements
            payload = self._format_review_request(code_changes)

            response = requests.post(
                f"{self.settings.AI_SERVICE_URL}/review",
                headers=headers,
                json=payload,
                timeout=30,  # 30 seconds timeout
            )
            response.raise_for_status()

            return self._process_review_response(response.json())

        except requests.exceptions.RequestException as e:
            return {
                "status": "failed",
                "error": f"AI review service error: {str(e)}",
                "suggestions": [],
                "summary": "Failed to complete code review",
            }

    def _format_review_request(
        self, code_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format code changes for the AI service API

        Args:
            code_changes: List of code changes to format

        Returns:
            Formatted payload for the AI service
        """
        return {
            "files": [
                {
                    "path": change["file_path"],
                    "content": change["changes"],
                    "author": change["author"],
                    "context": change.get("jira_context", {}),
                }
                for change in code_changes
            ],
            "settings": {
                "language": "python",
                "style_guide": "pep8",
                "complexity_threshold": "medium",
            },
        }

    def _process_review_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the AI service response

        Args:
            response_data: Raw response from the AI service

        Returns:
            Processed and validated review results
        """
        # Ensure required fields are present
        required_fields = ["status", "suggestions", "summary"]
        if not all(field in response_data for field in required_fields):
            return {
                "status": "failed",
                "error": "Invalid response from AI service",
                "suggestions": [],
                "summary": "Failed to process AI review results",
            }

        return {
            "status": "success",
            "suggestions": response_data["suggestions"],
            "summary": response_data["summary"],
        }
