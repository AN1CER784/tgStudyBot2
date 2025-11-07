import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from constants.on_going_messages import BEFORE_ENTRY_TEST_MESSAGE
from database.crud.user import create_or_update_user_stage, get_user
from keyboards.user_keyboards import continue_keyboard
from services.checkout_user import user_checkout, staff_checkout
from utils.get_human_sex import get_sex_human

logger = logging.getLogger(__name__)


async def finalize_registration(message: Message, state: FSMContext, phone: str | None):
    if not phone:
        await message.answer("Не удалось распознать номер. Попробуйте снова отправить контакт или вписать вручную.")
        return

    data = await state.get_data()
    full_name = data.get("full_name", "—")
    dob = data.get("dob", "")
    sex = data.get("sex", "")
    checkout = await user_checkout(message)
    if checkout:
        return
    if not full_name or not dob or not sex or not phone:
        await message.answer("Не удалось получить данные. Попробуйте снова. Введите /start чтобы начать регистрацию заново")
    user = await get_user(user_id=message.from_user.id)
    user.full_name = full_name
    user.birthday = dob
    user.phone = phone
    user.sex = sex
    await user.save()
    await create_or_update_user_stage(user_id=message.from_user.id, stage='entry_test')
    await message.answer(
        f"✅ Вы зарегистрировались:\n"
        f"• Фамилия, Имя: {full_name}\n"
        f"• Дата рождения: {dob:%d.%m.%Y}\n"
        f"• Телефон: {phone} \n"
        f"• Пол: {get_sex_human(user.sex)}",
        reply_markup=ReplyKeyboardRemove()
    )

    logger.info(f"User {message.from_user.id} registered as {full_name} with phone {phone}, birthday: {dob}, sex: {sex}")
    await state.clear()

    checkout_on_staff = await staff_checkout(user=user, message=message)
    if checkout_on_staff:
        return
    await message.answer(BEFORE_ENTRY_TEST_MESSAGE,
                         reply_markup=continue_keyboard('entry_test', "🟢 Начать входной тест"))
