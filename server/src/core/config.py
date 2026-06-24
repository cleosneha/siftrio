import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "siftrio"
    PROJECT_VERSION: str = "0.1.0"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL") or "http://localhost:3000"
    BACKEND_URL: str = os.getenv("BACKEND_URL") or "http://localhost:8000"
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_project_memory"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or "postgres"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER") or "localhost"
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT") or "5432"
    POSTGRES_DB: str = os.getenv("POSTGRES_DB") or "ai_project_memory"
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY") or ""
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID") or ""
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET") or ""
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or ""
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES") or "15")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS") or "30")
    FIREFLIES_API_KEY: str = os.getenv("FIREFLIES_API_KEY") or ""
    FIREFLIES_WEBHOOK_SECRET: str = os.getenv("FIREFLIES_WEBHOOK_SECRET") or ""

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("+asyncpg", "")

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()

if settings.MISTRAL_API_KEY:
    os.environ["MISTRAL_API_KEY"] = settings.MISTRAL_API_KEY
