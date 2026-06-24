from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.auth_controller import AuthController
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


@router.post("/refresh", response_model=BaseResponse)
async def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        return BaseResponse(success=False, message="Refresh token not found")

    service = AuthService(AuthRepository(db))
    new_access_token = await service.refresh_access_token(refresh_token)
    if not new_access_token:
        return BaseResponse(success=False, message="Invalid or expired refresh token")

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )
    return BaseResponse(message="Token refreshed successfully")


@router.post("/logout", response_model=BaseResponse)
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh")
    return BaseResponse(message="Logged out successfully")
