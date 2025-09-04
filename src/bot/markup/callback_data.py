from aiogram.filters.callback_data import CallbackData


class MenuAction(CallbackData, prefix="menu"):
    action: str


class EntryAction(CallbackData, prefix="entry"):
    action: str
    entry_id: int


class PaginatedMenuAction(CallbackData, prefix="page"):
    action: str
    page: int


class PaginatedEntryAction(CallbackData, prefix="page"):
    action: str
    entry_id: int | None
    page: int


class TypedEntryAction(CallbackData, prefix="tentry"):
    action: str
    entry_id: int
    entry_type: str


class DataAction(CallbackData, prefix="data"):
    action: str
    data: str
