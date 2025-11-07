from aiogram.fsm.state import StatesGroup, State


class LessonAnswerSG(StatesGroup):
    waiting = State()