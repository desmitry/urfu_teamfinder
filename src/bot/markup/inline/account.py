from typing import Iterable
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder
import src.core.postgres.bot as tb
from src.bot.markup.callback_data import (
    CallbackData, MenuAction, EntryAction,
    DataAction, PaginatedMenuAction, PaginatedEntryAction
)


def paginated_menu_builder(
    action: str,
    action_entry_id: int | None,
    back_action: CallbackData,
    page: int,
    last_page: int,
    i18n: I18n,
    locale: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(
            text="<",
            callback_data=PaginatedEntryAction(
                action=action,
                entry_id=action_entry_id,
                page=page-1
            ) if action_entry_id is not None else PaginatedMenuAction(
                action=action,
                page=page-1
            )
        )
    if page < last_page:
        builder.button(
            text=">",
            callback_data=PaginatedEntryAction(
                action=action,
                entry_id=action_entry_id,
                page=page+1
            ) if action_entry_id is not None else PaginatedMenuAction(
                action=action,
                page=page+1
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "general.button.back",
                locale=locale
            ),
            callback_data=back_action.pack()
        )
    )
    return builder


def main_menu(
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "main_menu.button.browse",
                locale=locale
            ),
            callback_data=PaginatedMenuAction(
                action="show_account_list",
                page=0
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "main_menu.button.account_menu",
                locale=locale
            ),
            callback_data=MenuAction(
                action="show_account_menu"
            ).pack()
        )
    )
    return builder.as_markup()


def account_menu(
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "account_menu.button.set_image",
                locale=locale
            ),
            callback_data=MenuAction(
                action="ask_account_image"
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "account_menu.button.set_name",
                locale=locale
            ),
            callback_data=MenuAction(
                action="ask_account_full_name"
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "account_menu.button.set_description",
                locale=locale
            ),
            callback_data=MenuAction(
                action="ask_account_description"
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "account_menu.button.my_tags",
                locale=locale
            ),
            callback_data=MenuAction(
                action="show_account_tag_list"
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "general.button.back",
                locale=locale
            ),
            callback_data=MenuAction(
                action="show_main_menu"
            ).pack()
        )
    )
    return builder.as_markup()


def account_list(
    account: tb.Account,
    accounts: Iterable[tb.Account],
    page: int,
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    target_account: tb.Account = accounts[page]
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "account_list.button.unlike",
                locale=locale
            ) if target_account.id in [l.liked_account_id for l in account.likes] else i18n.gettext(
                "account_list.button.like",
            ),
            callback_data=EntryAction(
                action="toggle_account_like",
                entry_id=target_account.id
            ).pack()
        )
    )
    builder.attach(
        paginated_menu_builder(
            "show_account_list",
            None,
            MenuAction(
                action="show_main_menu"
            ),
            page,
            len(accounts) - 1,
            i18n,
            locale
        )
    )
    return builder.as_markup()


def account_tag_list(
    tags: Iterable[tb.Tag],
    account_tags: Iterable[tb.AccountTag],
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in tags:
        prefix = ""
        if tag.id in [at.tag.id for at in account_tags]:
            prefix = "✅ "
        builder.row(
            InlineKeyboardButton(
                text=prefix + tag.title,
                callback_data=EntryAction(
                    action="toggle_account_tag",
                    entry_id=tag.id
                ).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "general.button.back",
                locale=locale
            ),
            callback_data=MenuAction(
                action="show_account_menu"
            ).pack()
        ),
        InlineKeyboardButton(
            text=i18n.gettext(
                "general.button.home",
                locale=locale
            ),
            callback_data=MenuAction(
                action="show_main_menu"
            ).pack()
        )
    )
    return builder.as_markup()


def registration_menu(
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "registration_menu.button.student",
                locale=locale
            ),
            callback_data=DataAction(
                action="set_account_type",
                data="student"
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "registration_menu.button.mentor",
                locale=locale
            ),
            callback_data=DataAction(
                action="set_account_type",
                data="mentor"
            ).pack()
        )
    )
    return builder.as_markup()
