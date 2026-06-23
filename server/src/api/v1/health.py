from fastapi import APIRouter

from src.core.config import settings
from src.core.database_check import check_database_connection
from src.schemas.base_response import BaseResponse
from src.schemas.health_schema import HealthCheckData, HealthRootData

router = APIRouter(tags=["health"])


@router.get("/", response_model=BaseResponse[HealthRootData])
async def root() -> BaseResponse[HealthRootData]:
    return BaseResponse(
        data=HealthRootData(
            project=settings.PROJECT_NAME,
            version=settings.PROJECT_VERSION,
            status="healthy",
        ),
    )


@router.get("/health", response_model=BaseResponse[HealthCheckData])
async def health() -> BaseResponse[HealthCheckData]:
    db_status: str = "connected" if await check_database_connection() else "disconnected"
    return BaseResponse(
        data=HealthCheckData(
            status="healthy",
            database=db_status,  # type: ignore[arg-type]
        ),
    )
