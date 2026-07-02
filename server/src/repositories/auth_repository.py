from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.user_integration import UserIntegration


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_google_id(self, google_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        full_name: str | None,
        profile_picture: str | None,
        google_id: str,
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            profile_picture=profile_picture,
            google_id=google_id,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        from datetime import datetime, timezone

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.last_login_at = datetime.now(timezone.utc)

    async def get_integration(self, user_id: UUID, provider: str) -> UserIntegration | None:
        result = await self.db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_integration(
        self,
        user_id: UUID,
        provider: str,
        access_token: str,
        refresh_token: str | None,
        token_expires_at: object | None,
        scopes: str | None,
    ) -> UserIntegration:
        existing = await self.get_integration(user_id, provider)
        if existing:
            existing.access_token = access_token
            if refresh_token is not None:
                existing.refresh_token = refresh_token
            existing.token_expires_at = token_expires_at
            existing.scopes = scopes
        else:
            integration = UserIntegration(
                user_id=user_id,
                provider=provider,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                scopes=scopes,
            )
            self.db.add(integration)

        await self.db.flush()
        result = await self.get_integration(user_id, provider)
        return result
