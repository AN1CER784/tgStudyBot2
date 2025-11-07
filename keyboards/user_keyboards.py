from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from constants.callbacks import USER_ED_PHONE, USER_ED_BACK, USER_ED_FULL_NAME, USER_ED_DOB, USER_OPEN_DOB, \
    USER_SEX_WOMAN, USER_SEX_MAN, USER_ED_SEX
from constants.tests import ABC
from database.models.test import Option


def continue_keyboard(prefix: str, continue_text: str = "Продолжить ➜"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{continue_text}', callback_data=f'continue:{prefix}')
            ]
        ]
    )


def build_options_kb(prefix: str, options: List[Option], attempt_id: int, question_id: int) -> InlineKeyboardMarkup:
    # Берём максимум 4 варианта в порядке order
    opts = sorted(options, key=lambda o: o.order)[:4]
    rows = []
    for letter, opt in zip(ABC, opts):
        rows.append(
            [InlineKeyboardButton(text=letter, callback_data=f"{prefix}:ans:{attempt_id}:{question_id}:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[
            [KeyboardButton(text="📱 Отправить телефон", request_contact=True)],
            [KeyboardButton(text="✍️ Ввести номер вручную")]
        ],
    )


def reopen_dob_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Открыть календарь снова", callback_data=USER_OPEN_DOB)]]
    )


def edit_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Изменить Фамилию, Имя", callback_data=USER_ED_FULL_NAME)],
        [InlineKeyboardButton(text="📅 Изменить дату рождения", callback_data=USER_ED_DOB)],
        [InlineKeyboardButton(text="📱 Изменить телефон", callback_data=USER_ED_PHONE)],
        [InlineKeyboardButton(text="🛠 Редактировать пол", callback_data=USER_ED_SEX)],
        [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data=USER_ED_BACK)],
    ])


def choice_sex_kb(prefix) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🦰 Мужской", callback_data=f"{prefix}:{USER_SEX_MAN}"),
         InlineKeyboardButton(text="👩‍🦱 Женский", callback_data=f"{prefix}:{USER_SEX_WOMAN}")]
    ])


def attachments_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Отправить ответ", callback_data="attach_done"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="attach_cancel")]
    ])


def feedback_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Отправить отзыв", callback_data="feedback_done"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="feedback_cancel")]
    ])


def feedback_prompt_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Отправить отзыв", callback_data="feedback_done"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="feedback_skip")]
    ])


def personal_data_agreement_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="personal_data_agreement_yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data="personal_data_agreement_no")]
    ])
