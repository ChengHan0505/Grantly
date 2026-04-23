from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Grantly"
    app_version: str = "1.0.0"
    allowed_origins: list[str] = ["*"]
    model_name: str = "ilmu-glm-5.1"


settings = Settings()
