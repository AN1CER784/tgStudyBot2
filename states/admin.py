from aiogram.fsm.state import StatesGroup, State


class AdminPickUserSG(StatesGroup):
    grant_access = State()
    grant_curator = State()
    grant_admin = State()
