from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory


async def check_database_connection() -> bool:
    try:
        async with async_session_factory() as session:
            session: AsyncSession
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
