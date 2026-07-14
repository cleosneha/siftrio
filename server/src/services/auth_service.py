import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from src.core.config import settings
from src.repositories.auth_repository import AuthRepository
from src.schemas.auth_schema import UserResponse
from src.integrations.google_oauth import (
    fetch_token,
    get_google_profile,
    refresh_google_token,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    async def handle_google_callback(self, code: str) -> tuple[UserResponse, str, str]:
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

        existing_integration = await self.repo.get_integration(user.id, "google")
        google_refresh_token = (
            token_data.get("refresh_token")
            or (existing_integration.refresh_token if existing_integration else None)
        )

        await self.repo.upsert_integration(
            user_id=user.id,
            provider="google",
            access_token=token_data["access_token"],
            refresh_token=google_refresh_token,
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

        access_token = self._create_access_token(user.id, user.email)
        refresh_token = self._create_refresh_token(user.id, user.email)

        logger.info("User %s logged in via Google - refresh_token stored: %s", user.id, bool(token_data.get("refresh_token")))

        return user_resp, access_token, refresh_token

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

    def _create_access_token(self, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
            "type": "access",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def _create_refresh_token(self, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now,
            "type": "refresh",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def _decode_token(token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.PyJWTError:
            return None

    @staticmethod
    def validate_jwt(token: str) -> dict | None:
        return AuthService._decode_token(token)

    @staticmethod
    def validate_access_token(token: str) -> dict | None:
        payload = AuthService._decode_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None

    @staticmethod
    def validate_refresh_token(token: str) -> dict | None:
        payload = AuthService._decode_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None

    async def refresh_access_token(self, refresh_token_str: str) -> str | None:
        payload = self.validate_refresh_token(refresh_token_str)
        if not payload:
            return None
        user = await self.repo.get_user_by_id(UUID(payload["user_id"]))
        if not user:
            return None
        return self._create_access_token(user.id, user.email)

    async def get_valid_google_access_token(self, user_id: UUID) -> str | None:
        integration = await self.repo.get_integration(user_id, "google")
        if not integration or not integration.access_token:
            return None

        now = datetime.now(timezone.utc)
        if integration.token_expires_at and integration.token_expires_at > now:
            return integration.access_token

        if not integration.refresh_token:
            logger.warning("Google refresh token missing for user %s", user_id)
            return None

        token_data = await refresh_google_token(integration.refresh_token)
        if not token_data:
            logger.error("Failed to refresh Google token for user %s", user_id)
            return None

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
        await self.repo._db.commit()

        return token_data["access_token"]
