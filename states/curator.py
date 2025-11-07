from aiogram.fsm.state import StatesGroup, State


class CuratorCommentLessonSG(StatesGroup):
    waiting = State()


class CuratorCommentFinalSG(StatesGroup):
    waiting = State()
