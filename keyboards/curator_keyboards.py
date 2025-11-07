from typing import Iterable, TypeVar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tortoise import Model

from constants.callbacks import CUR_OPEN_PREFIX, CUR_LIST_PREFIX, CUR_OK_PREFIX, CUR_REJECT_PREFIX, \
    CUR_LIST_FINAL_PREFIX, \
    ADMIN_MAIN, CUR_COMMENT_FINAL_PREFIX, CURATOR_MENU
from database.crud.user import PAGE_SIZE

from utils.pager import build_pager

SM = TypeVar('SM', bound=Model)


def curator_list_kb(items: Iterable[SM], page: int, total: int, callback_list: str = CUR_LIST_PREFIX,
                    callback_row: str = CUR_OPEN_PREFIX) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"#{item.id} {item.user.full_name}",
                                  callback_data=f"{callback_row}:{item.id}")]
            for item in items]
    rows += build_pager(callback_list, page, total, PAGE_SIZE)
    rows += [[InlineKeyboardButton(text="⬅️ Назад", callback_data=CURATOR_MENU)]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def curator_detail_kb(response_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"{CUR_OK_PREFIX}:{response_id}"),
            InlineKeyboardButton(text="❌ Вернуть", callback_data=f"{CUR_REJECT_PREFIX}:{response_id}"),
        ],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data=f"{CUR_LIST_PREFIX}:0")],
    ])


def curator_final_comment_kb(attempt_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Прокомментировать прохождение курса",
                                 callback_data=f"{CUR_COMMENT_FINAL_PREFIX}:{attempt_id}"),
        ],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data=f"{CUR_LIST_PREFIX}:0")],
    ])


def curator_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Список заданий на проверку", callback_data=CUR_LIST_PREFIX)],
        [InlineKeyboardButton(text="📈 Список для оценки прохождение курса", callback_data=CUR_LIST_FINAL_PREFIX)],
        [InlineKeyboardButton(text="⬅️ Вернуться в админ панель", callback_data=ADMIN_MAIN)] if is_admin else []
    ])
