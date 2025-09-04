from aiogram.filters.state import State, StatesGroup


class MenuState(StatesGroup):
    Menu = State()


class Dialogue(StatesGroup):
    AccountFullName = State()
    AccountDescription = State()
    AccountImage = State()

    AnnouncementText = State()
