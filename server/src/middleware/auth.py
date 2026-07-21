import logging
import time
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)


async def require_authenticated_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> None:
    t0 = time.perf_counter()

    token = access_token
    if not token:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = AuthService.validate_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    t1 = time.perf_counter()

    service = AuthService(AuthRepository(db))
    user = await service.get_user_by_id(UUID(payload["user_id"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    t2 = time.perf_counter()

    logger.info(
        "Auth timing — JWT: %.2fms | DB: %.2fms | Total: %.2fms",
        (t1 - t0) * 1000,
        (t2 - t1) * 1000,
        (t2 - t0) * 1000,
    )

    request.state.user = user
