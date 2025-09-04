from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.bot.markup.callback_data import MenuAction


def popup(
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=i18n.gettext(
                "general.button.hide",
                locale=locale
            ),
            callback_data=MenuAction(
                action="close_popup"
            ).pack()
        )
    )
    return builder.as_markup()


def account_link(
    target_account
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=target_account.full_name,
            url=f"tg://user?id={target_account.chat_id}"
        )
    )
    return builder.as_markup()
