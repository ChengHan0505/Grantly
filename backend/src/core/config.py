from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Grantly"
    app_version: str = "1.0.0"
    app_description: str = (
        "Malaysia SME Grant Copilot API for onboarding, company profile extraction, "
        "grant scouting, evaluator matching, readiness coaching, drafter generation, "
        "and submission package assembly."
    )
    allowed_origins: list[str] = ["*"]
    model_name: str = Field(
        default="claude-sonnet-4-5-20250929",
        validation_alias=AliasChoices("MODEL_NAME", "CLAUDE_SONNET_MODEL", "GEMINI_MODEL", "GOOGLE_MODEL"),
    )
    claude_sonnet_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("CLAUDE_SONNET_API_KEY", "ANTHROPIC_API_KEY"),
    )
    claude_sonnet_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        validation_alias=AliasChoices("CLAUDE_SONNET_MODEL", "ANTHROPIC_MODEL"),
    )
    claude_sonnet_base_url: str = Field(
        default="https://api.anthropic.com/v1",
        validation_alias=AliasChoices("CLAUDE_SONNET_BASE_URL", "ANTHROPIC_BASE_URL"),
    )
    google_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "GOOGLE_MODEL", "MODEL_NAME"),
    )
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    openrouter_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "OPENROUTER_API_KEY",
            "OPENROUTER_GEMINI_API_KEY",
        ),
    )
    openrouter_model: str = Field(
        default="google/gemini-2.5-flash",
        validation_alias=AliasChoices("OPENROUTER_MODEL", "OPENROUTER_GEMINI_MODEL"),
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias=AliasChoices("OPENROUTER_BASE_URL"),
    )
    zai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("ZAI_API_KEY", "Z_AI_API_KEY", "ZHIPUAI_API_KEY", "ILMU_API_KEY"),
    )
    zai_model: str = Field(
        default="ilmu-glm-5.1",
        validation_alias=AliasChoices("ZAI_MODEL", "GLM_MODEL"),
    )
    zai_base_url: str = Field(
        default="https://api.ilmu.ai/v1",
        validation_alias=AliasChoices("ZAI_BASE_URL", "GLM_BASE_URL"),
    )
    readiness_threshold_percent: int = 80
    scout_enabled: bool = True
    scout_max_pages_per_source: int = 12
    scout_max_links_per_page: int = 10
    scout_max_chars_per_page: int = 8000
    scout_max_runtime_hours: float = 8.0
    scout_http_timeout_seconds: int = 20
    scout_user_agent: str = "GrantlyScout/1.0 (+https://grantly.local)"
    scout_source_file: str = "backend/data/scout_sources.json"
    scout_respect_robots_txt: bool = True
    scout_request_delay_seconds: float = 1.0
    scout_results_dir: str = "backend/data/scout_runs"
    scout_report_path: str = "backend/data/scout_runs/last_report.json"


settings = Settings()
