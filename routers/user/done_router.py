import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.user_keyboards import feedback_kb
from utils.edit_message import update_host_message

logger = logging.getLogger(__name__)

router = Router(name="done_router")


@router.callback_query(F.data == "continue:done")
async def done_handle(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(host_mid=callback.message.message_id)
    await update_host_message(callback.message, state, "🎉 Курс пройден!")
    await callback.message.answer('Вы можете оставить отзыв о курсе!', reply_markup=feedback_kb())
    await state.clear()
    logger.info(f"User {callback.from_user.id} finished course")
