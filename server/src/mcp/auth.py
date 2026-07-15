import hashlib
import logging
from datetime import datetime, timezone

from mcp.server.auth.provider import AccessToken, TokenVerifier
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models.api_key import ApiKey
from src.models.workspace_member import WorkspaceMember

logger = logging.getLogger(__name__)


class ApiKeyVerifier(TokenVerifier):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def verify_token(self, token: str) -> AccessToken | None:
        hashed = hashlib.sha256(token.encode()).hexdigest()

        async with self._session_factory() as db:
            result = await db.execute(
                select(ApiKey).where(ApiKey.hashed_secret == hashed)
            )
            api_key = result.scalar_one_or_none()

            if api_key is None:
                return None

            if api_key.revoked_at is not None:
                logger.warning("Revoked API key used: %s", api_key.id)
                return None

            api_key.last_used_at = datetime.now(timezone.utc)
            await db.commit()

            ws_result = await db.execute(
                select(WorkspaceMember.workspace_id).where(
                    WorkspaceMember.user_id == api_key.user_id
                )
            )
            workspace_ids = [str(row[0]) for row in ws_result.fetchall()]

            logger.info(
                "API key authenticated: user=%s key=%s workspaces=%d",
                api_key.user_id,
                api_key.id,
                len(workspace_ids),
            )

            return AccessToken(
                token=token,
                client_id=str(api_key.user_id),
                scopes=["mcp:read"],
                claims={
                    "user_id": str(api_key.user_id),
                    "workspace_ids": workspace_ids,
                },
            )
