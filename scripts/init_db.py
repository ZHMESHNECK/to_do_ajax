from db.base import Base
from db.session import engine


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )