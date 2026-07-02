from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.auth_controller import AuthController
from src.core.config import settings
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.repositories.auth_repository import AuthRepository
from src.schemas.base_response import BaseResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login(db: AsyncSession = Depends(get_db)):
    controller = AuthController(db)
    return await controller.login()


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    controller = AuthController(db)
    return await controller.callback(code)


@router.get("/me", response_model=BaseResponse, dependencies=[Depends(require_authenticated_user)])
async def get_me(request: Request):
    return BaseResponse(data=request.state.user.model_dump())


@router.post("/refresh")
async def refresh_token(
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        return JSONResponse(
            status_code=200,
            content=BaseResponse(success=False, message="Refresh token not found").model_dump(),
        )

    service = AuthService(AuthRepository(db))
    new_access_token = await service.refresh_access_token(refresh_token)
    if not new_access_token:
        return JSONResponse(
            status_code=200,
            content=BaseResponse(success=False, message="Invalid or expired refresh token").model_dump(),
        )

    resp = JSONResponse(
        content=BaseResponse(message="Token refreshed successfully").model_dump(),
    )
    resp.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return resp


@router.post("/logout")
async def logout():
    resp = JSONResponse(content=BaseResponse(message="Logged out successfully").model_dump())
    resp.delete_cookie(key="access_token", path="/")
    resp.delete_cookie(key="refresh_token", path="/api/auth/refresh")
    return resp
