import hashlib
import logging
from datetime import datetime, timezone

from mcp.server.auth.provider import AccessToken, TokenVerifier
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models.workspace_api_key import WorkspaceApiKey

logger = logging.getLogger(__name__)


class WorkspaceApiKeyVerifier(TokenVerifier):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def verify_token(self, token: str) -> AccessToken | None:
        hashed = hashlib.sha256(token.encode()).hexdigest()

        async with self._session_factory() as db:
            result = await db.execute(
                select(WorkspaceApiKey).where(
                    WorkspaceApiKey.hashed_secret == hashed
                )
            )
            api_key = result.scalar_one_or_none()

            if api_key is None:
                return None

            if api_key.revoked_at is not None:
                logger.warning("Revoked API key used: %s", api_key.id)
                return None

            api_key.last_used_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                "API key authenticated: workspace=%s user=%s key=%s",
                api_key.workspace_id,
                api_key.created_by,
                api_key.id,
            )

            return AccessToken(
                token=token,
                client_id=str(api_key.workspace_id),
                scopes=["mcp:read"],
                claims={
                    "workspace_id": str(api_key.workspace_id),
                    "user_id": str(api_key.created_by),
                },
            )
