import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery

from constants.on_going_messages import HI_MESSAGE_USER, PERSONAL_DATA_AGREEMENT
from database.crud.user import get_user
from keyboards.user_keyboards import continue_keyboard, personal_data_agreement_kb
from renderers.profile_renderer import stage_human
from services.checkout_user import user_checkout, staff_checkout
from states.registration import Registration

logger = logging.getLogger(__name__)

router = Router(name='start_router')


@router.message(CommandStart())
async def start(message: Message):
    checkout = await user_checkout(message)
    if checkout:
        return
    logger.info(f"User {message.from_user.id} started bot")
    doc = FSInputFile("docs/policy.pdf", filename="Согласие_на_обработку_перс_данных.pdf")
    await message.answer_document(document=doc)
    await message.answer(PERSONAL_DATA_AGREEMENT, reply_markup=personal_data_agreement_kb())


@router.callback_query(F.data == "personal_data_agreement_yes")
async def personal_data_agreement_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    logger.info(f'User {callback.from_user.id} agreed to personal data processing')
    await callback.message.edit_text(HI_MESSAGE_USER, reply_markup=continue_keyboard("registration"))


@router.callback_query(F.data == "personal_data_agreement_no")
async def personal_data_agreement_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    logger.info(f'User {callback.from_user.id} did not agree to personal data processing')
    await callback.message.edit_text(
        "Вы не согласились на обработку персональных данных, для повторного запуска бота можете ввести /start")


@router.message(Command('continue'))
async def continue_progress_cmd(message: Message, state: FSMContext):
    checkout = await user_checkout(message, registered_message=False)
    if not checkout:
        await message.answer("Вы не зарегистрированы, введите /start")
        return
    user = await get_user(message.from_user.id)
    checkout_on_staff = await staff_checkout(user=user, message=message)
    if checkout_on_staff:
        logger.info(f"Continue on staff user - {user.id}")
        return
    current_stage = user.progress.current_stage
    human_current_stage = stage_human(current_stage)
    logger.info(f"Continue user - {user.id} - {current_stage.value}")
    await message.answer(f"Текущий этап: {human_current_stage}\nПерейдите к нему нажав на кнопку",
                         reply_markup=continue_keyboard(f'{current_stage.value}', "➡️ Перейти к этапу"))


@router.callback_query(F.data == "continue:registration")
async def continue_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    logger.info(f"Start registration for user_id {callback.from_user.id}")
    await state.set_state(Registration.full_name)
    await callback.message.edit_text(
        "Для продолжения регистрации впишите свои фамилию и имя (например: Иванов Иван)"
    )
