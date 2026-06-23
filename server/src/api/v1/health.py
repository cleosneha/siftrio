from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.database_check import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "project": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "status": "healthy",
        }
    )


@router.get("/health")
async def health() -> JSONResponse:
    db_status = "connected" if await check_database_connection() else "disconnected"
    return JSONResponse(
        content={
            "status": "healthy",
            "database": db_status,
        }
    )
