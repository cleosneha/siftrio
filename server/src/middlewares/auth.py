from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService


async def require_authenticated_user(
    request: Request,
    response: Response,
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

    service = AuthService(AuthRepository(db))

    payload = AuthService.validate_jwt(token)
    if payload:
        user_id = payload["user_id"]
    else:
        expired_payload = AuthService.decode_jwt_safe(token)
        if expired_payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user_id = expired_payload["user_id"]
        new_token = await service.refresh_jwt(user_id)
        if new_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired, please login again",
            )

        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
            path="/",
        )

    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    request.state.user = user
