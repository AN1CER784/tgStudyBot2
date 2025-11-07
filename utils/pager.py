from aiogram.types import InlineKeyboardButton


def build_pager(prefix: str, page: int, total: int, page_size: int) -> list[list[InlineKeyboardButton]]:
    pages = max(1, (total + page_size - 1) // page_size)
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(text="⟨ Назад", callback_data=f"{prefix}:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page + 1 < pages:
        row.append(InlineKeyboardButton(text="Вперёд ⟩", callback_data=f"{prefix}:{page + 1}"))
    return [row]
