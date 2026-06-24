from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.auth_controller import AuthController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse

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


@router.post("/logout", response_model=BaseResponse)
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return BaseResponse(message="Logged out successfully")
