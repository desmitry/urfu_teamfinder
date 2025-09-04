from aiogram import F
from aiogram.types import ChatMemberUpdated, CallbackQuery
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    MEMBER, KICKED
)
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound
from sqlalchemy import update
from src.bot.markup.callback_data import MenuAction
from src.bot.logic.adapter import DbAdapter
import src.core.postgres.bot as tb
from src.bot.logic.entities import menu_router, simple_router


menu_router.my_chat_member.filter(F.chat.type == "private")


@menu_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def account_blocked_bot(
    event: ChatMemberUpdated,
    db: DbAdapter
):
    await db.session.execute(
        update(tb.Account)
        .where(
            tb.Account.chat_id == event.from_user.id
        )
        .values(
            is_active=False
        )
    )
    await db.commit()


@menu_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def account_unblocked_bot(
    event: ChatMemberUpdated,
    db: DbAdapter
):
    await db.session.execute(
        update(tb.Account)
        .where(
            tb.Account.chat_id == event.from_user.id
        )
        .values(
            is_active=True
        )
    )
    await db.commit()


@simple_router.callback_query(
    MenuAction.filter(
        F.action == "close_popup"
    )
)
async def close_popup(
    query: CallbackQuery,
):
    try:
        await query.message.delete()
    except (TelegramBadRequest, TelegramNotFound):
        pass
