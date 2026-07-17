import logging

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.exceptions.base import BaseAPIException
from src.privacy.reporting_service import PersonalDataReportingService
from src.schemas.base_response import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["privacy-cron"])


def _verify_cron_secret(authorization: str | None = Header(None)) -> None:
    if not settings.CRON_SECRET:
        raise BaseAPIException(
            message="CRON_SECRET not configured",
            status_code=500,
        )
    if authorization != f"Bearer {settings.CRON_SECRET}":
        raise BaseAPIException(
            message="Unauthorized",
            status_code=401,
        )


@router.post(
    "/cron/privacy/report",
    response_model=BaseResponse,
    dependencies=[Depends(_verify_cron_secret)],
)
async def cron_privacy_report(
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = PersonalDataReportingService(db)
    result = await service.report_and_process()
    return BaseResponse(message="Privacy report completed", data=result)
