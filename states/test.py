from aiogram.fsm.state import StatesGroup, State


class EntryTestSG(StatesGroup):
    answering = State()


class FinalTestSG(StatesGroup):
    answering = State()
