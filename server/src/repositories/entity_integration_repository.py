from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.entity_integration import EntityIntegration


class EntityIntegrationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get(
        self,
        entity_type: str,
        entity_id: UUID,
        provider: str,
    ) -> EntityIntegration | None:
        result = await self._db.execute(
            select(EntityIntegration).where(
                EntityIntegration.entity_type == entity_type,
                EntityIntegration.entity_id == entity_id,
                EntityIntegration.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> list[EntityIntegration]:
        result = await self._db.execute(
            select(EntityIntegration).where(
                EntityIntegration.entity_type == entity_type,
                EntityIntegration.entity_id == entity_id,
            )
        )
        return list(result.scalars().all())

    async def get_by_provider(
        self,
        entity_type: str,
        provider: str,
        external_ids: list[str],
    ) -> list[EntityIntegration]:
        result = await self._db.execute(
            select(EntityIntegration).where(
                EntityIntegration.entity_type == entity_type,
                EntityIntegration.provider == provider,
                EntityIntegration.external_id.in_(external_ids),
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        entity_type: str,
        entity_id: UUID,
        provider: str,
        external_id: str | None = None,
        external_key: str | None = None,
        external_url: str | None = None,
        external_type: str | None = None,
        sync_status: str | None = None,
        external_assignee_id: str | None = None,
        extra_data: dict | None = None,
    ) -> EntityIntegration:
        integration = EntityIntegration(
            entity_type=entity_type,
            entity_id=entity_id,
            provider=provider,
            external_id=external_id,
            external_key=external_key,
            external_url=external_url,
            external_type=external_type,
            sync_status=sync_status,
            external_assignee_id=external_assignee_id,
            extra_data=extra_data,
        )
        self._db.add(integration)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def upsert(
        self,
        entity_type: str,
        entity_id: UUID,
        provider: str,
        external_id: str | None = None,
        external_key: str | None = None,
        external_url: str | None = None,
        external_type: str | None = None,
        sync_status: str | None = None,
        external_assignee_id: str | None = None,
        extra_data: dict | None = None,
    ) -> EntityIntegration:
        existing = await self.get(entity_type, entity_id, provider)
        if existing:
            if external_id is not None:
                existing.external_id = external_id
            if external_key is not None:
                existing.external_key = external_key
            if external_url is not None:
                existing.external_url = external_url
            if external_type is not None:
                existing.external_type = external_type
            if sync_status is not None:
                existing.sync_status = sync_status
            if external_assignee_id is not None:
                existing.external_assignee_id = external_assignee_id
            if extra_data is not None:
                existing.extra_data = extra_data
            await self._db.flush()
            await self._db.refresh(existing)
            return existing
        return await self.create(
            entity_type=entity_type,
            entity_id=entity_id,
            provider=provider,
            external_id=external_id,
            external_key=external_key,
            external_url=external_url,
            external_type=external_type,
            sync_status=sync_status,
            external_assignee_id=external_assignee_id,
            extra_data=extra_data,
        )

    async def delete(
        self,
        entity_type: str,
        entity_id: UUID,
        provider: str,
    ) -> None:
        existing = await self.get(entity_type, entity_id, provider)
        if existing:
            await self._db.delete(existing)
            await self._db.flush()
