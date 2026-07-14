import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import api_router
from src.core.config import settings
from src.exceptions.base import BaseAPIException
from src.exceptions.handlers import (
    base_exception_handler,
    global_exception_handler,
    jira_api_exception_handler,
    validation_exception_handler,
)
from src.integrations.atlassian.client import JiraAPIError
from fastapi.exceptions import RequestValidationError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
    )

    register_middleware(app)
    register_exception_handlers(app)
    register_routes(app)

    return app


def register_middleware(app: FastAPI) -> None:
    origins = list(set(settings.CORS_ORIGINS + [settings.FRONTEND_URL]))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    app.add_exception_handler(JiraAPIError, jira_api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)


def register_routes(app: FastAPI) -> None:
    prefix = f"/api"
    app.include_router(api_router, prefix=prefix)


app = create_app()
