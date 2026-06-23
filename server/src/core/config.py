import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "siftrio"
    PROJECT_VERSION: str = "0.1.0"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL") or "http://localhost:3000"
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_project_memory"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or "postgres"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER") or "localhost"
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT") or "5432"
    POSTGRES_DB: str = os.getenv("POSTGRES_DB") or "ai_project_memory"
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY") or ""

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
