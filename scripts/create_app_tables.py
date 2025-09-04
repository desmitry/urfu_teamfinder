import asyncio
from src.core.postgres.bot.engine import engine
from src.core.postgres.wrapper import Base


async def create_all():
    async with engine.begin() as session:
        # noinspection PyUnresolvedReferences
        await session.run_sync(Base.metadata.create_all)


asyncio.run(create_all())
