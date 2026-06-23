from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "siftrio"
    PROJECT_VERSION: str = "0.1.0"
    API_VERSION: str = "v1"
    FRONTEND_URL: str = "http://localhost:3000"
    DATABASE_URL: str | None = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "ai_project_memory"

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
