import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.integrations.atlassian.reporting_client import (
    AtlassianReportingClient,
    ReportingAPIError,
)
from src.integrations.atlassian.client import JiraClient
from src.models.jira_user import JiraUser
from src.repositories.jira_user_repository import JiraUserRepository
from src.repositories.workspace_jira_repository import WorkspaceJiraRepository
from src.services.workspace_jira_service import WorkspaceJiraService

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 90


class PersonalDataReportingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.workspace_jira_repo = WorkspaceJiraRepository(db)
        self.jira_user_repo = JiraUserRepository(db)
        self.workspace_jira_service = WorkspaceJiraService(db)

    async def report_and_process(self) -> dict:
        all_users = await self._get_all_jira_users()

        if not all_users:
            logger.info("[PRIVACY] Reporting run started — no Jira users stored")
            return {"reported": 0, "closed": 0, "updated": 0, "errors": 0}

        grouped = self._group_by_workspace(all_users)
        logger.info("[PRIVACY] Reporting run started — %d Jira users across %d workspaces", len(all_users), len(grouped))

        reported = 0
        closed = 0
        updated = 0
        errors = 0

        for workspace_id, users in grouped.items():
            try:
                integration = await self.workspace_jira_repo.get_by_workspace(workspace_id)
                if integration is None:
                    continue

                access_token = await self.workspace_jira_service.get_valid_access_token(workspace_id)
                client = AtlassianReportingClient(access_token)

                for batch_start in range(0, len(users), MAX_BATCH_SIZE):
                    batch = users[batch_start : batch_start + MAX_BATCH_SIZE]
                    accounts = [
                        {
                            "accountId": user.account_id,
                            "updatedAt": user.last_refreshed_at.strftime(
                                "%Y-%m-%dT%H:%M:%S.000Z",
                            ),
                        }
                        for user in batch
                    ]

                    try:
                        result = await client.report_accounts(accounts)
                        reported += len(batch)

                        if result["action_required"]:
                            for account in result["accounts"]:
                                action = account.get("status")
                                account_id = account.get("accountId")

                                if action == "closed":
                                    await self._erase_user(account_id)
                                    closed += 1
                                elif action == "updated":
                                    await self._refresh_user(
                                        account_id, workspace_id,
                                    )
                                    updated += 1

                    except ReportingAPIError as exc:
                        logger.error(
                            "[PRIVACY] Reporting API error for workspace %s: HTTP %d",
                            workspace_id, exc.status_code,
                        )
                        errors += 1

            except Exception as exc:
                logger.error(
                    "[PRIVACY] Failed to process workspace %s: %s",
                    workspace_id, exc,
                )
                errors += 1

        await self.db.commit()

        logger.info(
            "[PRIVACY] Reporting complete: reported=%d closed=%d updated=%d errors=%d",
            reported, closed, updated, errors,
        )

        return {
            "reported": reported,
            "closed": closed,
            "updated": updated,
            "errors": errors,
        }

    async def _get_all_jira_users(self) -> list[JiraUser]:
        result = await self.db.execute(select(JiraUser))
        return list(result.scalars().all())

    def _group_by_workspace(
        self, users: list[JiraUser],
    ) -> dict[UUID, list[JiraUser]]:
        grouped: dict[UUID, list[JiraUser]] = {}
        for user in users:
            grouped.setdefault(user.workspace_id, []).append(user)
        return grouped

    async def _erase_user(self, account_id: str) -> None:
        from src.models.knowledge_base import ActionItem

        result = await self.db.execute(
            select(ActionItem).where(
                ActionItem.jira_assignee_account_id == account_id,
            ),
        )
        items = result.scalars().all()

        for item in items:
            item.jira_assignee_account_id = None

        user = await self.jira_user_repo.get_by_account_id(account_id)
        if user:
            await self.jira_user_repo.delete(user)

        logger.warning(
            "[PRIVACY] Erased account ...%s (anonymized %d action items)",
            account_id[-4:], len(items),
        )

    async def _refresh_user(
        self, account_id: str, workspace_id: UUID,
    ) -> None:
        integration = await self.workspace_jira_repo.get_by_workspace(workspace_id)
        if integration is None or not integration.cloud_id:
            return

        try:
            access_token = await self.workspace_jira_service.get_valid_access_token(workspace_id)
            client = JiraClient(integration.cloud_id, access_token)

            raw = await client.search_users(account_id, global_search=True)
            user_data = None
            for u in raw:
                if u.get("accountId") == account_id:
                    user_data = u
                    break

            if user_data is None:
                return

            await self.jira_user_repo.get_or_create(
                account_id=account_id,
                workspace_id=workspace_id,
                display_name=user_data.get("displayName"),
                email_address=user_data.get("emailAddress"),
            )
            logger.warning("[PRIVACY] Refreshed account ...%s in workspace %s", account_id[-4:], workspace_id)

        except Exception as exc:
            logger.error(
                "[PRIVACY] Failed to refresh account ...%s in workspace %s: %s",
                account_id[-4:], workspace_id, exc,
            )
