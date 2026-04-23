from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Grantly"
    app_version: str = "1.0.0"
    allowed_origins: list[str] = ["*"]
    model_name: str = "GLM-5.1-Agentic"
    zai_api_key: str = "sk-89b4246651f62aafae76c6861dc72a5c1d7eb078b978c509"
    zai_model: str = "glm-4.5-flash"
    scout_enabled: bool = True
    scout_max_pages_per_source: int = 5
    scout_max_links_per_page: int = 20
    scout_max_chars_per_page: int = 8000
    scout_http_timeout_seconds: int = 20
    scout_user_agent: str = "GrantlyScout/1.0 (+https://grantly.local)"
    scout_results_dir: str = "data/scout_runs"
    scout_report_path: str = "data/scout_runs/last_report.json"
    model_name: str = "ilmu-glm-5.1"


settings = Settings()
