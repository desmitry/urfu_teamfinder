from typing import Iterable
from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import I18n

from src.core.postgres.wrapper import DbWrapper
import src.bot.text.account as txt
import src.bot.markup.inline as kb
import src.core.postgres.bot as tb


@dataclass
class ResponseData:
    text: str
    markup: InlineKeyboardMarkup
    file: bytes | None = None


class DbAdapter(DbWrapper):
    # noinspection PyMethodMayBeStatic
    async def main_menu_response(
        self,
        i18n: I18n,
        locale: str
    ) -> ResponseData:
        return ResponseData(
            i18n.gettext(
                "main_menu.text",
                locale=locale
            ),
            kb.main_menu(
                i18n,
                locale
            )
        )

    async def account_menu_response(
        self,
        account_chat_id: int | tb.Account,
        i18n: I18n,
        locale: str
    ) -> ResponseData:
        account: tb.Account
        if isinstance(account_chat_id, tb.Account):
            account = account_chat_id
        else:
            account = (
                await self.scalars(
                    tb.Account,
                    tb.Account.chat_id == account_chat_id,
                    join=(
                        (
                            tb.Account.account_tags,
                            tb.AccountTag.tag
                        ),
                    )
                )
            ).unique().one()
        return ResponseData(
            txt.account_menu(
                account
            ),
            kb.account_menu(
                i18n,
                locale
            ),
            account.image
        )

    async def account_list_response(
        self,
        account_chat_id: int | tb.Account,
        page: int,
        i18n: I18n,
        locale: str
    ) -> ResponseData:
        accounts: Iterable[tb.Account] = []
        account: tb.Account
        if isinstance(account_chat_id, tb.Account):
            account = account_chat_id
        else:
            account = (
                await self.scalars(
                    tb.Account,
                    tb.Account.chat_id == account_chat_id,
                    join=(
                        (
                            tb.Account.likes,
                        ),
                    )
                )
            ).one()
        match account.type:
            case "mentor":
                likes = (
                    await self.scalars(
                        tb.Like,
                        tb.Like.liked_account_id == account.id,
                        join=(
                            (
                                tb.Like.liker_account.of_type(tb.Student),
                                tb.Student.account_tags,
                                tb.AccountTag.tag
                            ),
                        )
                    )
                ).unique().all()
                accounts = [l.liker_account for l in likes if l.liker_account.is_active]
            case "student":
                accounts = (
                    await self.scalars(
                        tb.Mentor,
                        tb.Mentor.is_active == True,
                        join=(
                            (
                                tb.Mentor.account_tags,
                                tb.AccountTag.tag
                            ),
                        )
                    )
                ).unique().all()

        # Sort by relevance
        sorting_table: list[tuple[tb.Account, int]] = []
        for t in accounts:
            c = 0
            for tag_id in [tag.id for tag in account.account_tags]:
                if tag_id in [tag.id for tag in t.account_tags]:
                    c += 1
            sorting_table.append((t, c))
        sorting_table.sort(key=lambda x: x[1], reverse=True)
        accounts = [i[0] for i in sorting_table]

        target_account: tb.Account = accounts[page]
        text = txt.account_menu(
            target_account
        )
        return ResponseData(
            text,
            kb.account_list(
                account,
                accounts,
                page,
                i18n,
                locale
            ),
            account.image
        )

    async def account_tag_list_response(
        self,
        account_chat_id: int | tb.Account,
        i18n: I18n,
        locale: str
    ) -> ResponseData:
        account: tb.Account
        if isinstance(account_chat_id, tb.Account):
            account = account_chat_id
        else:
            account = (
                await self.scalars(
                    tb.Account,
                    tb.Account.chat_id == account_chat_id,
                    join=(
                        (
                            tb.Account.account_tags,
                            tb.AccountTag.tag
                        ),
                    )
                )
            ).unique().one()
        tags: Iterable[tb.Tag] = (
            await self.scalars(
                tb.Tag
            )
        ).all()
        return ResponseData(
            i18n.gettext(
                "account_tag_list.text",
                locale=locale
            ),
            kb.account_tag_list(
                tags,
                account.account_tags,
                i18n,
                locale
            )
        )
