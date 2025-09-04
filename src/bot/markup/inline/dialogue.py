from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.bot.logic.states import State, Dialogue
from src.bot.markup.callback_data import MenuAction


def question(
    state: State,
    i18n: I18n,
    locale: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    match state:
        case (
            Dialogue.AccountImage
            | Dialogue.AccountDescription
            | Dialogue.AccountFullName
        ):
            builder.row(
                InlineKeyboardButton(
                    text=i18n.gettext(
                        "general.button.back",
                        locale=locale
                    ),
                    callback_data=MenuAction(
                        action="end_dialogue"
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
