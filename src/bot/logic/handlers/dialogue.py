from typing import Any
from aiogram import F
from aiogram.types import CallbackQuery, InputMediaPhoto, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n
from src.bot.logic.states import MenuState
from src.bot.logic.adapter import DbAdapter, ResponseData
from src.bot.markup.callback_data import MenuAction
from src.bot.logic.entities import menu_router


@menu_router.callback_query(
    MenuAction.filter(
        F.action == "end_dialogue"
    )
)
async def end_dialogue(
    query: CallbackQuery,
    state: FSMContext,
    state_data: dict[str, Any],
    db: DbAdapter,
    i18n: I18n,
):
    response_data: ResponseData
    match (await state.get_state()).split(":")[1]:
        case "AccountFullName" | "AccountDescription" | "AccountImage":
            response_data = await db.account_menu_response(
                query.from_user.id,
                i18n,
                state_data["locale"]
            )
    await state.set_state(MenuState.Menu)
    # noinspection PyUnboundLocalVariable
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
