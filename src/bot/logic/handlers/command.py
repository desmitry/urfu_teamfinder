from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from src.bot.logic.states import MenuState
from src.bot.logic.entities import command_router
from src.bot.logic.adapter import DbAdapter
import src.core.postgres.bot as tb
import src.bot.markup.inline as kb


@command_router.message(CommandStart())
async def register_account_send_main_menu(
    message: Message,
    state: FSMContext,
    db: DbAdapter,
    i18n: I18n,
    i18n_middleware: FSMI18nMiddleware
):
    await message.delete()
    locale: str
    account: tb.Account = (
        await db.scalars(
            tb.Account,
            tb.Account.chat_id == message.from_user.id
        )
    ).first()
    answer: Message
    text: str
    markup: InlineKeyboardMarkup
    if not account:
        user_full_name: str = ""
        if message.from_user.first_name:
            user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
        account = tb.Account(
            type="account",
            chat_id=message.from_user.id,
            full_name=user_full_name
        )
        db.add(account)
        await db.flush()
        if message.from_user.language_code in i18n.available_locales:
            await i18n_middleware.set_locale(state, message.from_user.language_code)
        else:
            await i18n_middleware.set_locale(state, "ru")
    await db.update_account_bio(
        account,
        message.from_user.username
    )
    locale = (await state.get_data())["locale"]
    await state.set_state(MenuState.Menu)
    await db.commit()
    if account.type == "account":
        text = i18n.gettext(
            "registration_menu.text",
            locale=locale
        )
        markup = kb.registration_menu(i18n, locale)
    else:
        text = i18n.gettext(
            "main_menu.text",
            locale=locale
        )
        markup = kb.main_menu(i18n, locale)
    answer = await message.answer_photo(
        FSInputFile(
            "src/bot/assets/logo.jpeg"
        ),
        caption=text,
        reply_markup=markup
    )
    await state.update_data(
        {
            "menu_message_id": answer.message_id,
            "entry_data": {
                "page": None
            }
        }
    )
