from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService


async def require_authenticated_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> None:
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

    service = AuthService(AuthRepository(db))
    user = await service.get_user_by_id(UUID(payload["user_id"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    request.state.user = user
