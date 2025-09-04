import asyncio
from src.core.postgres.bot.engine import open_db_session
import src.core.postgres.bot.models as tb


async def main():
    async with open_db_session() as session:
        # Specify and insert tags
        tags = (
            "Frontend-Разработка", "Backend-Разработка", "Мобильная Разработка",
            "Машинное Обучение", "Анализ Данных", "Математика", "Физика",
            "Английский Язык", "Gamedev"
        )
        for tag in tags:
            session.add(tb.Tag(title=tag))
        await session.commit()


asyncio.run(main())
