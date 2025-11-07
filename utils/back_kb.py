from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{prefix}")]
    ])
