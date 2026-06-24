import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.base import BaseAPIException
from src.schemas.base_response import ErrorResponse

logger = logging.getLogger(__name__)


async def base_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            errors=exc.errors,
        ).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors: list[dict[str, Any]] = [
        {"field": ".".join(map(str, err["loc"])), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Validation error",
            errors=errors,
        ).model_dump(),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
        ).model_dump(),
    )
