"""Database connectivity utility.

Usage:
    python database.py

Prints "Database connected successfully" if the connection works.
"""

import asyncio

import asyncpg

from src.core.config import settings


async def main() -> None:
    url = settings.database_url
    dsn = url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("SELECT 1")
        print("Database connected successfully")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
