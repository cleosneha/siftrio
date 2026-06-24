from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService
from src.tools.google_oauth import get_authorization_url
from src.core.config import settings


class AuthController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = AuthService(AuthRepository(db))

    async def login(self) -> RedirectResponse:
        url = get_authorization_url()
        return RedirectResponse(url=url)

    async def callback(self, code: str) -> RedirectResponse:
        try:
            user, jwt_token = await self.service.handle_google_callback(code)
        except ValueError:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=true")

        response = RedirectResponse(url=settings.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
            path="/",
        )
        return response
