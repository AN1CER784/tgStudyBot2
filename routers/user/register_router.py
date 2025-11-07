from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import get_user_locale, DialogCalendarCallback, \
    DialogCalendar

from keyboards.user_keyboards import contact_keyboard, choice_sex_kb
from services.profile_service import phone_text_handle, phone_contact_handle, handle_calendar_process, reopen_calendar, \
    full_name_handle
from services.registration_service import finalize_registration
from states.registration import Registration

router = Router(name='register_router')


@router.message(StateFilter(Registration.full_name))
async def handle_full_name(message: Message, state: FSMContext):
    full_name = await full_name_handle(message)
    if not full_name:
        return
    await state.update_data(full_name=full_name)
    await state.set_state(Registration.dob)

    cal = DialogCalendar(locale="ru_RU.utf8")
    await message.answer("Выберите дату рождения:", reply_markup=await cal.start_calendar())


# ЕДИНЫЙ обработчик коллбэков календаря:
@router.callback_query(StateFilter(Registration.dob), DialogCalendarCallback.filter())
async def on_calendar(callback: CallbackQuery,
                      callback_data: DialogCalendarCallback,
                      state: FSMContext):
    picked_date = await handle_calendar_process(callback, callback_data)
    if not picked_date:
        return
    await state.update_data(dob=picked_date)
    await state.set_state(Registration.sex)
    await callback.message.edit_text(
        f"Дата рождения: {picked_date:%d.%m.%Y}\nТеперь выберите пол.", reply_markup=choice_sex_kb('registration')
    )


# 2) Обработчик кнопки «Открыть календарь снова»
@router.callback_query(StateFilter(Registration.dob), F.data == "dob_open")
async def reopen_dob(callback: CallbackQuery):
    await reopen_calendar(callback)


@router.callback_query(F.data.startswith('registration:sex'), StateFilter(Registration.sex))
async def handle_sex(callback: CallbackQuery, state: FSMContext):
    sex = callback.data.split(':')[-1]
    await state.update_data(sex=sex)
    await state.set_state(Registration.phone)
    await callback.message.delete()
    await callback.message.answer("Отправьте номер телефона:", reply_markup=contact_keyboard())
    await callback.answer('Выберите действие')


@router.message(StateFilter(Registration.phone), F.contact)
async def handle_contact(message: Message, state: FSMContext):
    """Пользователь отправил контакт через кнопку"""
    phone = await phone_contact_handle(message)
    if not phone:
        return
    await finalize_registration(message, state, phone)


@router.message(StateFilter(Registration.phone))
async def handle_phone_text(message: Message, state: FSMContext):
    """Ввод телефона вручную"""
    phone = await phone_text_handle(message)
    if not phone:
        return
    await finalize_registration(message, state, phone)
