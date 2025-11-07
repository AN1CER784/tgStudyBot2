from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram_calendar import get_user_locale, DialogCalendar, DialogCalendarCallback

from constants.callbacks import USER_ED_FULL_NAME, USER_ED_BACK, USER_ED_DOB, USER_OPEN_DOB, USER_ED_PHONE, USER_ED_SEX
from database.crud.user import get_user
from keyboards.user_keyboards import edit_menu_kb, contact_keyboard, choice_sex_kb
from services.profile_service import phone_text_handle, phone_contact_handle, handle_calendar_process, \
    reopen_calendar, full_name_handle, update_phone,  show_profile
from states.edit import EditProfileSG
from utils.get_human_sex import get_sex_human
import logging

logger = logging.getLogger(__name__)

router = Router(name="profile_router")


@router.message(Command('profile'))
async def cmd_profile(message: Message | None = None, callback: CallbackQuery | None = None):
    await show_profile(message, message.from_user.id)


@router.message(Command("edit"))
async def cmd_edit(message: Message):
    await message.answer("Что хотите изменить?", reply_markup=edit_menu_kb())


@router.callback_query(F.data == USER_ED_BACK)
async def edit_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data == USER_ED_FULL_NAME)
async def edit_fio_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditProfileSG.full_name)
    await callback.message.edit_text("Введите новые Фамилию, имя (например: Иванов Иван)")


@router.message(EditProfileSG.full_name)
async def edit_full_name_save(message: Message, state: FSMContext):
    full_name = await full_name_handle(message)
    if not full_name:
        return
    user = await get_user(message.from_user.id)
    user.full_name = full_name
    await user.save()
    await state.clear()
    await message.answer(f"Фамилия, имя обновлены ✅", reply_markup=ReplyKeyboardRemove())
    logger.info(f"User {message.from_user.id} updated full name to {full_name}")
    await show_profile(message, message.from_user.id)


# ---- Дата рождения (DialogCalendar) ----
@router.callback_query(F.data == USER_ED_DOB)
async def edit_dob_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditProfileSG.dob)
    await reopen_calendar(callback)


@router.callback_query(EditProfileSG.dob, DialogCalendarCallback.filter())
async def edit_dob_pick(callback: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    picked_date = await handle_calendar_process(callback, callback_data)
    if not picked_date:
        return
    user = await get_user(callback.from_user.id)
    user.birthday = picked_date
    await user.save()
    await state.clear()
    await callback.message.answer(f"Дата рождения обновлена: {picked_date:%d.%m.%Y} ✅")
    logger.info(f"User {callback.from_user.id} updated DOB to {picked_date}")
    await show_profile(callback.message, callback.from_user.id)


# «переоткрыть» календарь, если закрыли
@router.callback_query(EditProfileSG.dob, F.data == USER_OPEN_DOB)
async def edit_dob_reopen(callback: CallbackQuery):
    cal = DialogCalendar(locale=await get_user_locale(callback.from_user))
    await callback.message.answer("Календарь снова открыт 👇", reply_markup=await cal.start_calendar())


# ---- Пол ----
@router.callback_query(F.data == USER_ED_SEX)
async def edit_sex_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите пол:", reply_markup=choice_sex_kb("edit"))


@router.callback_query(F.data.startswith("edit:sex"))
async def edit_sex(callback: CallbackQuery, state: FSMContext):
    sex = callback.data.split(':')[-1]
    user = await get_user(callback.from_user.id)
    user.sex = sex
    await user.save()
    await state.clear()
    await callback.message.edit_text(f"Пол обновлён: {get_sex_human(sex)} ✅")
    logger.info(f"User {callback.from_user.id} updated sex to {sex}")
    await show_profile(callback.message, callback.from_user.id)


# ---- Телефон ----
@router.callback_query(F.data == USER_ED_PHONE)
async def edit_phone_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditProfileSG.phone)
    await callback.message.edit_text("Отправьте контакт кнопкой ниже или введите номер в формате +79991234567.")
    await callback.message.answer("Жду номер телефона:", reply_markup=contact_keyboard())


@router.message(EditProfileSG.phone, F.contact)
async def edit_phone_contact(message: Message, state: FSMContext):
    phone = await phone_contact_handle(message)
    if not phone:
        return
    await update_phone(message, state, phone)
    logger.info(f"User {message.from_user.id} updated phone to {phone}")
    await show_profile(message, message.from_user.id)


@router.message(EditProfileSG.phone)
async def edit_phone_text(message: Message, state: FSMContext):
    phone = await phone_text_handle(message)
    if not phone:
        return
    await update_phone(message, state, phone)
    logger.info(f"User {message.from_user.id} updated phone to {phone}")
    await show_profile(message, message.from_user.id)
