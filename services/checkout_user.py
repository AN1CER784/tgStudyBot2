from typing import Optional

from aiogram.types import Message

from config import ADMINS
from constants.callbacks import ADMIN_MAIN, CURATOR_MENU
from database.crud.user import get_user
from database.models import UserProgress, User
from keyboards.user_keyboards import continue_keyboard


async def user_checkout(message: Message, registered_message: bool = True) -> bool:
    user = await get_user(message.from_user.id)
    if user and user.progress:
        if user.progress.current_stage != "start" and user.phone and user.full_name and user.sex:
            if registered_message:
                await message.answer("Вы уже зарегистрированы. Для продолжения нажмите /continue")
            return True


async def check_user_stage(user_id: int, stage: str, stage_index: int | None = None) -> Optional[
    tuple[bool, UserProgress]]:
    user = await get_user(user_id)
    if user and user.progress:
        if user.progress.current_stage == stage:
            if stage_index is not None and user.progress.stage_index != stage_index:
                return
            return True, user.progress


async def staff_checkout(user: User, message: Message):
    if user.role == 'admin' or user.id in ADMINS:
        await message.answer("Вы администратор. Вам доступны следующие функции.",
                             reply_markup=continue_keyboard(ADMIN_MAIN))
        return True
    elif user.role == 'curator':
        await message.answer("Вы куратор. Вам доступны следующие функции.",
                             reply_markup=continue_keyboard(CURATOR_MENU))
        return True
