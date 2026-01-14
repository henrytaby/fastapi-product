import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "AppTransactionFastAPI"
    VERSION: str = "v1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Utils
    TIME_ZONE: int
    PROJECT_ROOT: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Audit
    ENABLE_ACCESS_AUDIT: bool = True
    ENABLE_DATA_AUDIT: bool = True
    AUDIT_EXCLUDED_PATHS: list[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "GET:/health",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
