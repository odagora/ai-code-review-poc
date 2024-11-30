from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Jira configuration
    JIRA_URL: str
    JIRA_USERNAME: str
    JIRA_API_TOKEN: str
    JIRA_PROJECT_KEY: str = "AIREV"  # Default project key

    # Git configuration
    REPO_PATH: Optional[str] = None

    # AI Service configuration
    AI_SERVICE_URL: Optional[str] = None
    AI_SERVICE_API_KEY: Optional[str] = None

    # Application configuration
    APP_NAME: str = "AI Code Review"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def get_jira_cloud_url(self) -> str:
        """Format Jira Cloud URL correctly"""
        base_url = self.JIRA_URL.rstrip("/")
        if not base_url.startswith("https://"):
            base_url = f"https://{base_url}"
        if not base_url.endswith("atlassian.net"):
            base_url = f"{base_url}.atlassian.net"
        return base_url

    @property
    def jira_api_url(self) -> str:
        """Get the full Jira API URL"""
        return f"{self.get_jira_cloud_url()}/rest/api/3"

    def validate_jira_config(self) -> None:
        """Validate Jira configuration"""
        if not all([self.JIRA_URL, self.JIRA_USERNAME, self.JIRA_API_TOKEN]):
            raise ValueError("Missing required Jira configuration")
        if "@" not in self.JIRA_USERNAME:
            raise ValueError("JIRA_USERNAME must be an email address")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    settings.validate_jira_config()
    return settings
