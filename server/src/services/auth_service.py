from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from src.core.config import settings
from src.repositories.auth_repository import AuthRepository
from src.schemas.auth_schema import UserResponse
from src.tools.google_oauth import (
    fetch_token,
    get_google_profile,
    refresh_google_token,
)


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    async def handle_google_callback(self, code: str) -> tuple[UserResponse, str]:
        token_data = await fetch_token(code)
        profile = await get_google_profile(token_data["access_token"])
        if not profile:
            raise ValueError("Failed to fetch Google profile")

        google_id = profile["id"]
        email = profile["email"]
        full_name = profile.get("name")
        picture = profile.get("picture")

        user = await self.repo.get_user_by_google_id(google_id)
        if not user:
            user = await self.repo.get_user_by_email(email)

        if user:
            user.google_id = google_id
            user.full_name = full_name or user.full_name
            user.profile_picture = picture or user.profile_picture
        else:
            user = await self.repo.create_user(
                email=email,
                full_name=full_name,
                profile_picture=picture,
                google_id=google_id,
            )

        await self.repo.upsert_integration(
            user_id=user.id,
            provider="google",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=(
                datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
                if token_data.get("expires_at")
                else None
            ),
            scopes=token_data.get("scope"),
        )

        await self.repo.update_last_login(user.id)

        user_resp = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            profile_picture=user.profile_picture,
        )

        jwt_token = self._create_jwt(user.id, user.email)

        return user_resp, jwt_token

    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            return None
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            profile_picture=user.profile_picture,
        )

    async def refresh_user_google_token(self, user_id: UUID) -> bool:
        integration = await self.repo.get_integration(user_id, "google")
        if not integration or not integration.refresh_token:
            return False

        now = datetime.now(timezone.utc)
        if integration.token_expires_at and integration.token_expires_at > now:
            return True

        token_data = await refresh_google_token(integration.refresh_token)
        if not token_data:
            return False

        await self.repo.upsert_integration(
            user_id=user_id,
            provider="google",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token") or integration.refresh_token,
            token_expires_at=(
                datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
                if token_data.get("expires_at")
                else None
            ),
            scopes=token_data.get("scope") or integration.scopes,
        )

        return True

    def _create_jwt(self, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def validate_jwt(token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def decode_jwt_safe(token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
            return payload
        except jwt.InvalidTokenError:
            return None

    async def refresh_jwt(self, user_id: UUID) -> str | None:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            return None

        integration = await self.repo.get_integration(user_id, "google")
        if not integration:
            return None

        if integration.refresh_token:
            now = datetime.now(timezone.utc)
            if integration.token_expires_at and integration.token_expires_at < now:
                token_data = await refresh_google_token(integration.refresh_token)
                if token_data:
                    await self.repo.upsert_integration(
                        user_id=user_id,
                        provider="google",
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token") or integration.refresh_token,
                        token_expires_at=(
                            datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
                            if token_data.get("expires_at")
                            else None
                        ),
                        scopes=token_data.get("scope") or integration.scopes,
                    )

        return self._create_jwt(user.id, user.email)
