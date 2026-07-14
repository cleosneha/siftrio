import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.integrations.atlassian import (
    fetch_token,
    get_accessible_resources,
    get_authorization_url,
    is_token_expired,
    refresh_access_token,
)
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.repositories.workspace_jira_repository import WorkspaceJiraRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.jira_schema import WorkspaceJiraResponse

logger = logging.getLogger(__name__)


class WorkspaceJiraService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = WorkspaceJiraRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.project_jira_repo = ProjectJiraRepository(db)

    async def get_integration(self, workspace_id: UUID) -> dict | None:
        integration = await self.repo.get_by_workspace(workspace_id)
        if integration is None:
            return None
        await self.get_valid_access_token(workspace_id)
        integration = await self.repo.get_by_workspace(workspace_id)
        return WorkspaceJiraResponse.model_validate(integration).model_dump()

    async def get_or_create_oauth_url(self, workspace_id: UUID, user_id: UUID) -> str:
        integration = await self.repo.get_by_workspace(workspace_id)
        if integration is not None:
            if not is_token_expired(integration.token_expires_at.timestamp() if integration.token_expires_at else None):
                raise BaseAPIException(
                    message="Workspace already has a valid Jira integration",
                    status_code=400,
                )
            refreshed = await refresh_access_token(integration.refresh_token or "")
            if refreshed:
                expires_at_ts = refreshed.get("expires_at")
                new_expires_at = (
                    datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
                    if isinstance(expires_at_ts, (int, float))
                    else expires_at_ts
                )
                await self.repo.update(
                    integration,
                    access_token=refreshed["access_token"],
                    refresh_token=refreshed.get("refresh_token") or integration.refresh_token,
                    token_expires_at=new_expires_at,
                )
                await self.db.commit()
                return ""

        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise BaseAPIException(message="Workspace not found", status_code=404)

        return get_authorization_url(str(workspace_id))

    async def handle_callback(
        self,
        workspace_id: UUID,
        code: str,
        user_id: UUID,
    ) -> dict:
        token_data = await fetch_token(code)
        if token_data is None:
            raise BaseAPIException(
                message="Failed to authenticate with Atlassian",
                status_code=400,
            )

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_at_ts = token_data.get("expires_at")
        expires_at = (
            datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
            if isinstance(expires_at_ts, (int, float))
            else expires_at_ts
        )

        resources = await get_accessible_resources(access_token)
        if not resources:
            raise BaseAPIException(
                message="No accessible Atlassian sites found for this account",
                status_code=400,
            )

        cloud_id = resources[0]["id"]
        cloud_name = resources[0].get("name", "")
        site_url = resources[0].get("url", "")

        existing = await self.repo.get_by_workspace(workspace_id)
        if existing:
            integration = await self.repo.update(
                existing,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=expires_at,
                cloud_id=cloud_id,
                cloud_name=cloud_name,
                site_url=site_url,
                connected_by=user_id,
            )
        else:
            integration = await self.repo.create(
                workspace_id=workspace_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=expires_at,
                cloud_id=cloud_id,
                cloud_name=cloud_name,
                site_url=site_url,
                connected_by=user_id,
            )

        await self.db.commit()
        return WorkspaceJiraResponse.model_validate(integration).model_dump()

    async def refresh_token(self, workspace_id: UUID) -> dict:
        integration = await self.repo.get_by_workspace(workspace_id)
        if integration is None:
            raise BaseAPIException(
                message="Workspace has no Jira integration",
                status_code=400,
            )

        if not integration.refresh_token:
            raise BaseAPIException(
                message="No refresh token available. Reconnect Jira.",
                status_code=400,
            )

        token_data = await refresh_access_token(integration.refresh_token)
        if token_data is None:
            raise BaseAPIException(
                message="Failed to refresh token. Reconnect Jira.",
                status_code=400,
            )

        expires_at_ts = token_data.get("expires_at")
        expires_at = (
            datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
            if isinstance(expires_at_ts, (int, float))
            else expires_at_ts
        )
        integration = await self.repo.update(
            integration,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token") or integration.refresh_token,
            token_expires_at=expires_at,
        )
        await self.db.commit()
        return WorkspaceJiraResponse.model_validate(integration).model_dump()

    async def get_valid_access_token(self, workspace_id: UUID) -> str:
        integration = await self.repo.get_by_workspace(workspace_id)
        if integration is None:
            raise BaseAPIException(
                message="Workspace has no Jira integration",
                status_code=400,
            )

        expires_at = integration.token_expires_at
        now_ts = datetime.now(timezone.utc).timestamp()
        logger.warning(
            "[JIRA-TOKEN-DEBUG] workspace=%s token_expires_at=%s now=%s has_refresh_token=%s",
            workspace_id, expires_at, now_ts, bool(integration.refresh_token),
        )
        if expires_at is not None:
            logger.warning(
                "[JIRA-TOKEN-DEBUG] expires_at.timestamp()=%s diff_seconds=%s",
                expires_at.timestamp(), expires_at.timestamp() - now_ts,
            )

        should_refresh = (
            expires_at is None
            or is_token_expired(expires_at.timestamp())
        )
        logger.warning("[JIRA-TOKEN-DEBUG] should_refresh=%s", should_refresh)

        if should_refresh:
            if not integration.refresh_token:
                raise BaseAPIException(
                    message="Jira token expired and no refresh token available. Reconnect.",
                    status_code=400,
                )
            logger.warning("[JIRA-TOKEN-DEBUG] calling refresh_access_token...")
            token_data = await refresh_access_token(integration.refresh_token)
            if token_data is None:
                logger.error("[JIRA-TOKEN-DEBUG] refresh_access_token returned None!")
                raise BaseAPIException(
                    message="Failed to refresh Jira token. Reconnect.",
                    status_code=400,
                )
            logger.warning(
                "[JIRA-TOKEN-DEBUG] refresh succeeded, new_access_token=%.10s... expires_at=%s",
                token_data.get("access_token", ""),
                token_data.get("expires_at"),
            )
            expires_at_ts = token_data.get("expires_at")
            new_expires_at = (
                datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
                if isinstance(expires_at_ts, (int, float))
                else expires_at_ts
            )
            old_token = integration.access_token
            integration = await self.repo.update(
                integration,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token") or integration.refresh_token,
                token_expires_at=new_expires_at,
            )
            logger.warning(
                "[JIRA-TOKEN-DEBUG] old_token=%.10s... new_token=%.10s... new_expires_at=%s",
                old_token, integration.access_token, new_expires_at,
            )
            await self.db.commit()
            logger.warning("[JIRA-TOKEN-DEBUG] commit done")

        return integration.access_token

    async def get_sites(self, workspace_id: UUID) -> list[dict]:
        access_token = await self.get_valid_access_token(workspace_id)
        resources = await get_accessible_resources(access_token)
        return [
            {"id": r["id"], "name": r.get("name", ""), "url": r.get("url", "")}
            for r in resources
        ]

    async def disconnect(self, workspace_id: UUID) -> None:
        integration = await self.repo.get_by_workspace(workspace_id)
        if integration is None:
            raise BaseAPIException(
                message="Workspace has no Jira integration",
                status_code=400,
            )

        await self.repo.delete(integration)
