from aiogram.fsm.state import StatesGroup, State


class EditProfileSG(StatesGroup):
    full_name = State()
    dob = State()
    phone = State()
    sex = State()
