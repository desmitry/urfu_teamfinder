import asyncio
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
import src.bot.logic as l
from src.bot.logic.middlewares import (
    MenuVerifierMiddleware, DbAdapterMiddleware,
    StateDataGetterMiddleware
)
from src.bot.logic.utils import i18n
from src.core.postgres.bot.engine import open_db_session


async def main() -> None:

    l.command_router.message.middleware(FSMI18nMiddleware(i18n))
    l.command_router.message.middleware(DbAdapterMiddleware(open_db_session))

    l.menu_router.my_chat_member.middleware(StateDataGetterMiddleware())
    l.menu_router.my_chat_member.middleware(DbAdapterMiddleware(open_db_session))
    l.menu_router.callback_query.middleware(StateDataGetterMiddleware())
    l.menu_router.callback_query.middleware(FSMI18nMiddleware(i18n))
    l.menu_router.callback_query.middleware(MenuVerifierMiddleware())
    l.menu_router.callback_query.middleware(DbAdapterMiddleware(open_db_session))
    l.menu_router.message.middleware(StateDataGetterMiddleware())
    l.menu_router.message.middleware(FSMI18nMiddleware(i18n))
    l.menu_router.message.middleware(DbAdapterMiddleware(open_db_session))

    l.dispatcher.include_routers(
        l.command_router,
        l.menu_router,
        l.simple_router
    )
    await l.dispatcher.start_polling(l.bot)


asyncio.run(main())