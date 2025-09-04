import asyncio
from src.core.postgres.bot.engine import open_db_session
import src.core.postgres.bot.models as tb


async def main():
    async with open_db_session() as session:
        # Specify and insert tags
        ...
        await session.commit()


asyncio.run(main())
