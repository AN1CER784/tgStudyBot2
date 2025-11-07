import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram_calendar import DialogCalendar, DialogCalendarCallback
from aiogram_calendar.schemas import DialogCalAct

from constants.dob_dates import MIN_DOB, MAX_DOB
from database.crud.user import get_user
from keyboards.user_keyboards import reopen_dob_keyboard
from renderers.profile_renderer import render_profile
from utils.normalize_full_name import normalize_full_name
from utils.normalize_phone import normalize_phone

logger = logging.getLogger(__name__)


async def phone_text_handle(message: Message):
    text = (message.text or "").strip()
    if "ввести номер" in text.lower():
        await message.answer("Введите номер в формате +79991234567.")
        return

    phone = normalize_phone(text)
    if not phone:
        await message.answer("Не похоже на номер. Пример: +79991234567 (10–15 цифр). Попробуйте ещё раз.")
        return
    return phone


async def phone_contact_handle(message: Message):
    phone = normalize_phone(message.contact.phone_number)
    if not phone:
        await message.answer("Не удалось распознать номер. Попробуйте ещё раз.")
        return
    return phone


async def full_name_handle(message: Message):
    full_name = normalize_full_name(message.text)
    if not full_name:
        await message.answer("Похоже, вы не указали все верно. Укажите имя и фамилию на русском языке.")
        return
    return full_name


async def handle_calendar_process(callback: CallbackQuery,
                                  callback_data: DialogCalendarCallback):
    # 1) Ловим СТАНДАРТНЫЙ cancel от библиотеки (без своих кнопок)
    act = getattr(callback_data, "act", None)
    # Универсальная проверка для Enum/str):
    act_val = (getattr(act, "value", act) or "").lower()
    if act_val == "cancel" or (DialogCalAct and act == DialogCalAct.cancel):
        await callback.answer("Календарь закрыт")
        await callback.message.edit_text(
            "Календарь закрыт. Нажмите кнопку ниже, чтобы продолжить выбор даты:",
            reply_markup=reopen_dob_keyboard()
        )
        return

    # 2) Обычная обработка выбора/навигации
    cal = DialogCalendar(locale="ru_RU.utf8")
    cal.set_dates_range(MIN_DOB, MAX_DOB)
    selected, picked_date = await cal.process_selection(callback, callback_data)
    if not selected:
        return
    return picked_date


async def reopen_calendar(callback: CallbackQuery):
    cal = DialogCalendar(locale="ru_RU.utf8")
    await callback.message.edit_text("Выберите дату рождения:")
    await callback.message.answer("Календарь снова открыт 👇", reply_markup=await cal.start_calendar())
    await callback.answer()


async def update_phone(message: Message, state: FSMContext, phone: str):
    user = await get_user(message.from_user.id)
    user.phone = phone
    await user.save()
    await state.clear()
    await message.answer("Телефон обновлён ✅", reply_markup=ReplyKeyboardRemove())


async def show_profile(target: Message, actor_id: int):
    user = await get_user(actor_id)
    if not user:
        await target.answer("Вы не зарегистрированы в боте.\nВведите /start и завершите регистрацию")
        return
    await target.answer(await render_profile(user, user.progress))
    logger.info(f"Profile showed to user {user.id} - {user.full_name}")
