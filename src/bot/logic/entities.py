from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from src.core.config import settings


bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(
        parse_mode="HTML",
        protect_content=False
    )
)
storage = RedisStorage.from_url(
    f"redis://{settings.redis.host}:{settings.redis.port}?db={settings.redis.database}"
)
dispatcher = Dispatcher(storage=storage)
command_router = Router()
menu_router = Router()
simple_router = Router()
