from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Grantly"
    app_version: str = "1.0.0"
    app_description: str = (
        "Malaysia SME Grant Copilot API for onboarding, company profile extraction, "
        "grant scouting, evaluator matching, readiness coaching, drafter generation, "
        "and submission package assembly."
    )
    allowed_origins: list[str] = ["*"]
    model_name: str = "ilmu-glm-5.1"
    zai_api_key: str = ""
    zai_model: str = "glm-4.5-flash"
    readiness_threshold_percent: int = 80
    scout_enabled: bool = True
    scout_max_pages_per_source: int = 6
    scout_max_links_per_page: int = 5
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
