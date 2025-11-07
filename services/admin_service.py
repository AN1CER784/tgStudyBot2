from aiogram.types import Message

from config import ADMINS
from constants.callbacks import ADMIN_MAIN
from database.crud.user import get_user
from database.models.user import Roles
from utils.back_kb import back_button


async def admin_checkout(message: Message, cur_user_id, tg_to_change_id: int):
    if cur_user_id == tg_to_change_id:
        await message.edit_text("Нельзя менять самого себя", reply_markup=back_button(ADMIN_MAIN))
        return True
    user = await get_user(user_id=tg_to_change_id)
    if user.role == "admin":
        if (cur_user_id in ADMINS) and (tg_to_change_id not in ADMINS):
            return False
        await message.edit_text("Нельзя понизить админа в правах", reply_markup=back_button(ADMIN_MAIN))
        return True


async def is_admin_user(user_id: int):
    user = await get_user(user_id=user_id)
    if user.role == "admin" or user_id in ADMINS:
        return True
    return False


def get_role_match(role: Roles):
    mapping = {
        Roles.admin: "АДМИН",
        Roles.user: "ПОЛЬЗОВАТЕЛЬ",
        Roles.curator: "КУРАТОР"
    }
    return mapping.get(role, str(role.value))
