from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from src.core.config import settings


engine: AsyncEngine = create_async_engine(
    f"postgresql+asyncpg://{settings.postgres.username}:{settings.postgres.password}@{settings.postgres.host}:{settings.postgres.port}/{settings.app.database}", future=True
)
open_db_session = async_sessionmaker(engine)
