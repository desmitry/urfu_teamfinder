from typing import Any, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.bot.logic.adapter import DbAdapter
import src.core.postgres.bot.schema as tb


class MenuVerifierMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if event.message.message_id == data["state_data"]["menu_message_id"]:
            return await handler(event, data)
        else:
            return await event.answer(
                data["i18n"].gettext(
                    "general.query_answer.menu_expired",
                    locale=data["state_data"]["locale"]
                )
            )


class StateDataGetterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["state_data"] = await data["state"].get_data()
        return await handler(event, data)


class DbAdapterMiddleware(BaseMiddleware):
    def __init__(
            self,
            open_db_session: Callable[..., AsyncSession]
    ) -> None:
        self.open_db_session: Callable[..., AsyncSession] = open_db_session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.open_db_session() as session:
            data["db"] = DbAdapter(session)
            return await handler(event, data)
