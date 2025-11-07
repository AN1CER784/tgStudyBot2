from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    KeyboardButtonRequestUser

from constants.callbacks import ACCESS_MENU, ROLES_MENU, CURATOR_MENU, REQ_GRANT, ACCESS_LIST_PREFIX, ADMIN_MAIN, \
    REQ_ADMIN, REQ_CUR, ROLES_LIST_PREFIX, ACCESS_TOGGLE_PREFIX, ROLES_CHANGE_PREFIX, ROLES_SET_PREFIX, \
    USER_PROFILE_PREFIX, PROFILES_LIST_PREFIX
from database.crud.user import PAGE_SIZE
from services.admin_service import get_role_match
from utils.pager import build_pager


def role_change_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 ПОЛЬЗОВАТЕЛЬ", callback_data=f"{ROLES_SET_PREFIX}:{user_id}:user:0")],
        [InlineKeyboardButton(text="🎓 КУРАТОР", callback_data=f"{ROLES_SET_PREFIX}:{user_id}:curator:0")],
        [InlineKeyboardButton(text="👑 АДМИН", callback_data=f"{ROLES_SET_PREFIX}:{user_id}:admin:0")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{ROLES_LIST_PREFIX}:0")],
    ])


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Доступ к боту", callback_data=ACCESS_MENU)],
        [InlineKeyboardButton(text="🛡 Роли (админы/кураторы)", callback_data=ROLES_MENU)],
        [InlineKeyboardButton(text="🧑‍💻 Информация о пользователях", callback_data=f"{PROFILES_LIST_PREFIX}:0")],
        [InlineKeyboardButton(text="📋 Панель куратора", callback_data=CURATOR_MENU)],
    ])


def access_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Выдать доступ", callback_data=REQ_GRANT)],
        [InlineKeyboardButton(text="📃 Список с доступом", callback_data=f"{ACCESS_LIST_PREFIX}:0")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=ADMIN_MAIN)],
    ])


def roles_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Назначить АДМИНА", callback_data=REQ_ADMIN)],
        [InlineKeyboardButton(text="🎓 Назначить КУРАТОРА", callback_data=REQ_CUR)],
        [InlineKeyboardButton(text="🗂 Список ролей", callback_data=f"{ROLES_LIST_PREFIX}:0")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=ADMIN_MAIN)],
    ])


def request_user_kb(request_id: int, text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[KeyboardButton(text=text,
                                  request_user=KeyboardButtonRequestUser(request_id=request_id, user_is_bot=False))]],
    )


def allowed_item_row(user) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=f"{user.full_name or ''} ({user.id}) — доступ: {'да' if user.is_allowed else 'нет'}",
        callback_data=f"{ACCESS_TOGGLE_PREFIX}:{user.id}:{1 if user.is_allowed else 0}"
    )]


def user_item_row(user) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=f"{user.full_name or f'{user.id}'}",
        callback_data=f"{USER_PROFILE_PREFIX}:{user.id}"
    )]


def roles_item_row(user) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=f"{user.full_name or ''} ({user.id}) — роль: {get_role_match(user.role)}",
        callback_data=f"{ROLES_CHANGE_PREFIX}:{user.id}"
    )]


def pager_rows(prefix: str, page: int, total: int) -> list[list[InlineKeyboardButton]]:
    return build_pager(prefix, page, total, PAGE_SIZE)
