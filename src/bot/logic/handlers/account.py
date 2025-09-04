from typing import Any, Iterable

from aiogram import F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n

import src.core.postgres.bot as tb
import src.bot.text as txt
import src.bot.markup.inline as kb
from src.bot.logic.adapter import DbAdapter, ResponseData
from src.bot.logic.states import MenuState
from src.bot.markup.callback_data import MenuAction, EntryAction, DataAction, PaginatedMenuAction
from src.bot.logic.entities import menu_router


@menu_router.callback_query(
    DataAction.filter(
        F.action == "set_account_type"
    )
)
async def set_account_type_show_main_menu(
        query: CallbackQuery,
        state_data: dict[str, Any],
        callback_data: DataAction,
        db: DbAdapter,
        i18n: I18n
):
    account: tb.Account = (
        await db.scalars(
            tb.Account,
            query.from_user.id == tb.Account.chat_id
        )
    ).first()
    account.type = callback_data.data
    await db.commit()
    response_data: ResponseData = await db.main_menu_response(
        i18n,
        state_data["locale"]
    )
    await query.message.edit_caption(
        response_data.text,
        reply_markup=response_data.markup
    )
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "show_main_menu"
    )
)
async def show_main_menu(
    query: CallbackQuery,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    account: tb.Account = (
        await db.scalars(
            tb.Account,
            tb.Account.chat_id == query.from_user.id
        )
    ).one()
    handle: str | None = query.from_user.username
    if handle is not None:
        handle = handle.lower()
    account.handle = handle
    account.is_active = True
    await db.commit()
    response_data: ResponseData = await db.main_menu_response(
        i18n,
        state_data["locale"]
    )
    await query.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(
                "src/bot/assets/logo.jpeg"
            )
        )
    )
    await query.message.edit_caption(
        caption=response_data.text,
        reply_markup=response_data.markup
    )
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "show_account_menu"
    )
)
async def show_account_menu(
    query: CallbackQuery,
    state: FSMContext,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    response_data: ResponseData = await db.account_menu_response(
        query.from_user.id,
        i18n,
        state_data["locale"]
    )
    await state.set_state(MenuState.Menu)
    await state.update_data(
        {
            "entry_data": {
                "page": None
            }
        }
    )
    await query.message.edit_media(
        InputMediaPhoto(
            media=BufferedInputFile(
                response_data.file,
                "image"
            )
        )
    )
    await query.message.edit_caption(
        caption=response_data.text,
        reply_markup=response_data.markup
    )
    await query.answer()


@menu_router.callback_query(
    PaginatedMenuAction.filter(
        F.action == "show_account_list"
    )
)
async def show_account_list(
    query: CallbackQuery,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    response_data: ResponseData = await db.account_list_response(
        query.from_user.id,
        state_data["entry_data"]["page"],
        i18n,
        state_data["locale"]
    )
    await query.message.edit_media(
        InputMediaPhoto(
            media=BufferedInputFile(
                response_data.file,
                "image"
            )
        )
    )
    await query.message.edit_caption(
        caption=response_data.text,
        reply_markup=response_data.markup
    )


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "show_account_tag_list"
    )
)
async def show_account_tag_list(
    query: CallbackQuery,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    response_data: ResponseData = await db.account_tag_list_response(
        query.from_user.id,
        i18n,
        state_data["locale"]
    )
    await query.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(
                "src/bot/assets/logo.jpeg"
            )
        )
    )
    await query.message.edit_caption(
        caption=response_data.text,
        reply_markup=response_data.markup
    )
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "toggle_account_tag"
    )
)
async def toggle_account_tag(
    query: CallbackQuery,
    state_data: dict[str, Any],
    callback_data: EntryAction,
    db: DbAdapter,
    i18n: I18n
):
    tags: Iterable[tb.Tag] = (
        await db.scalars(
            tb.Tag
        )
    ).all()
    account: tb.Account = (
        await db.scalars(
            tb.Account,
            tb.Account.chat_id == query.from_user.id,
            join=(
                (
                    tb.Account.account_tags,
                    tb.AccountTag.tag
                ),
            )
        )
    ).unique().one()
    # Joined object list manipulation worked for me before
    # Rationale: flushing alone doesn't reflect changes in joined objects
    # Should work here too
    if callback_data.entry_id in [at.tag.id for at in account.account_tags]:
        for at in account.account_tags:
            if at.tag.id == callback_data.entry_id:
                await db.delete(at)
                account.account_tags.remove(at)
    else:
        account_tag = tb.AccountTag(
            account_id=account.id,
            tag_id=callback_data.entry_id
        )
        account_tag.tag = [t for t in tags if t.id == callback_data.entry_id][0]
        account.account_tags.append(account_tag)
        db.add(account_tag)
    await db.flush()
    await query.message.edit_media(
        InputMediaPhoto(
            media=BufferedInputFile(
                file=account.image,
                filename="image"
            )
        )
    )
    await query.message.edit_caption(
        caption=txt.account_tag_list(
            account,
            i18n,
            state_data["locale"]
        ),
        reply_markup=kb.account_tag_list(
            tags,
            account.account_tags,
            i18n,
            state_data["locale"]
        )
    )
    await db.commit()
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "toggle_account_like"
    )
)
async def toggle_account_like(
    query: CallbackQuery,
    state_data: dict[str, Any],
    callback_data: EntryAction,
    db: DbAdapter,
    i18n: I18n
):
    # TODO: Implement
    # Besides liking, match message sending should be here too (mentor branch)
    # Let's make the matching process one-sided for now
    ...
    await query.answer()
