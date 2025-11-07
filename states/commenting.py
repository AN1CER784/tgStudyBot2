from aiogram.fsm.state import StatesGroup, State


class ReviewSG(StatesGroup):
    waiting_text = State()
