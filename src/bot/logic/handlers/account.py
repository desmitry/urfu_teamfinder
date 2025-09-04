from typing import Any, Iterable

from aiogram import F, Bot
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, BufferedInputFile, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import StorageKey
from aiogram.utils.i18n import I18n
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import src.core.postgres.bot as tb
import src.bot.markup.inline as kb
from src.bot.logic.adapter import DbAdapter, ResponseData
from src.bot.logic.states import State, MenuState, Dialogue
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
        caption=response_data.text,
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
    state: FSMContext,
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
    await state.set_state(MenuState.Menu)
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
                "page": 0
            }
        }
    )
    if response_data.file:
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
    state: FSMContext,
    callback_data: PaginatedMenuAction,
    db: DbAdapter,
    i18n: I18n
):
    response_data: ResponseData = await db.account_list_response(
        query.from_user.id,
        callback_data.page,
        i18n,
        state_data["locale"]
    )
    await state.update_data(
        {
            "entry_data": {
                "page": callback_data.page
            }
        }
    )
    if response_data.file:
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
    EntryAction.filter(
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
    if callback_data.entry_id in [at.tag.id for at in account.account_tags]:
        for at in account.account_tags:
            if at.tag.id == callback_data.entry_id:
                await db.delete(at)
                account.account_tags.remove(at)
                break
    else:
        account_tag = tb.AccountTag(
            account_id=account.id,
            tag_id=callback_data.entry_id
        )
        account_tag.tag = [t for t in tags if t.id == callback_data.entry_id][0]
        account.account_tags.append(account_tag)
        db.add(account_tag)
    await db.flush()
    await query.message.edit_caption(
        caption=i18n.gettext(
            "account_tag_list.text",
            locale=state_data["locale"]
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
    EntryAction.filter(
        F.action == "toggle_account_like"
    )
)
async def toggle_account_like(
    query: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    state_data: dict[str, Any],
    callback_data: EntryAction,
    db: DbAdapter,
    i18n: I18n
):
    account: tb.Account = (
        await db.scalars(
            tb.Account,
            tb.Account.chat_id == query.from_user.id,
            join=(
                (
                    tb.Account.likes,
                    tb.Like.liker_account,
                    tb.Account.account_tags,
                    tb.AccountTag.tag
                ),
                (
                    tb.Account.liked_by,
                    tb.Like.liker_account,
                    tb.Account.account_tags,
                    tb.AccountTag.tag
                ),
                (
                    tb.Account.account_tags,
                    tb.AccountTag.tag
                )
            )
        )
    ).unique().one()
    target_account: tb.Account = (
        await db.scalars(
            tb.Account,
            tb.Account.id == callback_data.entry_id,
            join=(
                (
                    tb.Account.liked_by,
                ),
            )
        )
    ).unique().one()
    if account.id in [l.liker_account_id for l in target_account.liked_by]:
        for l in account.likes:
            if l.liked_account_id == target_account.id:
                await db.delete(l)
                break
        to_send = False
    else:
        like = tb.Like(
            liker_account_id=account.id,
            liked_account_id=target_account.id
        )
        db.add(like)
        to_send = True
    await db.flush()
    await db.session.refresh(account, ["likes"])
    await db.session.refresh(target_account, ["liked_by"])
    if to_send:
        match account.type:
            case "student":
                try:
                    locale: str = (
                        await state.storage.get_data(
                            StorageKey(
                                bot.id,
                                target_account.chat_id,
                                target_account.chat_id
                            )
                        )
                    )["locale"]
                    await bot.send_message(
                        chat_id=target_account.chat_id,
                        text=i18n.gettext(
                            "announcement.text.someone_liked_you",
                            locale=locale
                        ),
                        reply_markup=kb.popup(
                            i18n,
                            locale=locale
                        )
                    )
                except (KeyError, TelegramForbiddenError, TelegramBadRequest):
                    pass
            case "mentor":
                for a, ac in zip((target_account, account), (account, target_account)):
                    try:
                        locale: str = (
                            await state.storage.get_data(
                                StorageKey(
                                    bot.id,
                                    a.chat_id,
                                    a.chat_id
                                )
                            )
                        )["locale"]
                        await bot.send_message(
                            chat_id=a.chat_id,
                            text=i18n.gettext(
                                "announcement.text.match_found",
                                locale=locale
                            ),
                            reply_markup=kb.account_link(
                                ac
                            )
                        )
                    except (KeyError, TelegramForbiddenError, TelegramBadRequest):
                        pass
    response_data: ResponseData = await db.account_list_response(
        account,
        state_data["entry_data"]["page"],
        i18n,
        state_data["locale"]
    )
    await query.message.edit_caption(
        caption=response_data.text,
        reply_markup=response_data.markup
    )
    await db.commit()
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "ask_account_image"
    )
)
async def ask_account_image(
    query: CallbackQuery,
    state: FSMContext,
    state_data: dict[str, Any],
    i18n: I18n
):
    next_state: State = Dialogue.AccountImage
    await state.set_state(next_state)
    await query.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(
                "src/bot/assets/logo.jpeg"
            )
        )
    )
    await query.message.edit_caption(
        caption=i18n.gettext(
            "dialogue.account_image.text",
            locale=state_data["locale"]
        ),
        reply_markup=kb.question(
            next_state,
            i18n,
            state_data["locale"]
        )
    )
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "ask_account_full_name"
    )
)
async def ask_account_full_name(
    query: CallbackQuery,
    state: FSMContext,
    state_data: dict[str, Any],
    i18n: I18n
):
    next_state: State = Dialogue.AccountFullName
    await state.set_state(next_state)
    await query.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(
                "src/bot/assets/logo.jpeg"
            )
        )
    )
    await query.message.edit_caption(
        caption=i18n.gettext(
            "dialogue.account_full_name.text",
            locale=state_data["locale"]
        ),
        reply_markup=kb.question(
            next_state,
            i18n,
            state_data["locale"]
        )
    )
    await query.answer()


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "ask_account_description"
    )
)
async def ask_account_description(
    query: CallbackQuery,
    state: FSMContext,
    state_data: dict[str, Any],
    i18n: I18n
):
    next_state: State = Dialogue.AccountDescription
    await state.set_state(next_state)
    await query.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(
                "src/bot/assets/logo.jpeg"
            )
        )
    )
    await query.message.edit_caption(
        caption=i18n.gettext(
            "dialogue.account_description.text",
            locale=state_data["locale"]
        ),
        reply_markup=kb.question(
            next_state,
            i18n,
            state_data["locale"]
        )
    )
    await query.answer()


@menu_router.message(Dialogue.AccountFullName)
async def set_account_full_name_show_menu(
    message: Message,
    bot: Bot,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    await message.delete()
    if message.text is not None:
        account: tb.Account = (
            await db.scalars(
                tb.Account,
                tb.Account.chat_id == message.from_user.id,
                join=(
                    (
                        tb.Account.likes,
                    ),
                    (
                        tb.Account.account_tags,
                        tb.AccountTag.tag
                    ),
                )
            )
        ).unique().one()
        account.full_name = message.html_text
        response_data: ResponseData = await db.account_menu_response(
            account,
            i18n,
            state_data["locale"]
        )
        await db.commit()
        if response_data.file:
            await bot.edit_message_media(
                chat_id=message.from_user.id,
                message_id=state_data["menu_message_id"],
                media=InputMediaPhoto(
                    media=BufferedInputFile(
                        response_data.file,
                        filename="image"
                    )
                )
            )
        await bot.edit_message_caption(
            chat_id=message.from_user.id,
            message_id=state_data["menu_message_id"],
            caption=response_data.text,
            reply_markup=response_data.markup
        )


@menu_router.message(Dialogue.AccountDescription)
async def set_account_description_show_menu(
    message: Message,
    bot: Bot,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    await message.delete()
    if message.text is not None:
        account: tb.Account = (
            await db.scalars(
                tb.Account,
                tb.Account.chat_id == message.from_user.id,
                join=(
                    (
                        tb.Account.likes,
                    ),
                    (
                        tb.Account.account_tags,
                        tb.AccountTag.tag
                    ),
                )
            )
        ).unique().one()
        account.description = message.html_text
        response_data: ResponseData = await db.account_menu_response(
            account,
            i18n,
            state_data["locale"]
        )
        await db.commit()
        if response_data.file:
            await bot.edit_message_media(
                chat_id=message.from_user.id,
                message_id=state_data["menu_message_id"],
                media=InputMediaPhoto(
                    media=BufferedInputFile(
                        response_data.file,
                        filename="image"
                    ),
                )
            )
        await bot.edit_message_caption(
            chat_id=message.from_user.id,
            message_id=state_data["menu_message_id"],
            caption=response_data.text,
            reply_markup=response_data.markup
        )


@menu_router.message(Dialogue.AccountImage)
async def set_account_image_show_menu(
    message: Message,
    bot: Bot,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n
):
    await message.delete()
    if message.photo is not None:
        account: tb.Account = (
            await db.scalars(
                tb.Account,
                tb.Account.chat_id == message.from_user.id,
                join=(
                    (
                        tb.Account.likes,
                    ),
                    (
                        tb.Account.account_tags,
                        tb.AccountTag.tag
                    ),
                )
            )
        ).unique().one()
        with await bot.download(
                message.photo[-1].file_id
        ) as stream:
            image = stream.read()
        account.image = image
        response_data: ResponseData = await db.account_menu_response(
            account,
            i18n,
            state_data["locale"]
        )
        await db.commit()
        if response_data.file:
            await bot.edit_message_media(
                chat_id=message.from_user.id,
                message_id=state_data["menu_message_id"],
                media=InputMediaPhoto(
                    media=BufferedInputFile(
                        response_data.file,
                        filename="image"
                    ),
                )
            )
        await bot.edit_message_caption(
            chat_id=message.from_user.id,
            message_id=state_data["menu_message_id"],
            caption=response_data.text,
            reply_markup=response_data.markup
        )
