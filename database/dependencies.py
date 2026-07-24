from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .db import database


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in database.get_session():
        yield session