import src.core.postgres.bot as tb


def account_menu(
    account: tb.Account
) -> str:
    text = f"<b>{account.full_name}</b>"
    if account.description:
        text += "\n\n"
        text += f"{account.description}"
    if account.account_tags:
        text += "\n\n"
        text += "<b>" + ", ".join(at.tag.title for at in account.account_tags) + "</b>"
    return text
