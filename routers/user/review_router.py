import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton

from config import REVIEW_CHAT_ID
from database.crud.lesson import get_current_lesson
from services.checkout_user import check_user_stage
from services.lesson_service import send_lesson
from states.commenting import ReviewSG
from utils.send_message_safely import send_message_safely

logger = logging.getLogger(__name__)

router = Router(name="review_router")


async def _send_pending_lesson_if_any(message_or_cb, state: FSMContext):
    """Если в FSM задан pending_lesson_id — высылаем этот урок и чистим ключ."""
    checkout = await check_user_stage(message_or_cb.from_user.id, "lesson")
    if not checkout:
        return
    _stage, progress = checkout
    lesson = await get_current_lesson(progress)
    target_message = message_or_cb.message if isinstance(message_or_cb, CallbackQuery) else message_or_cb
    await send_lesson(target_message, lesson, progress, state)


@router.callback_query(F.data == "feedback_done")
async def feedback_done_handle(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReviewSG.waiting_text)
    await state.update_data(_lock=False)
    await callback.message.delete()
    await callback.message.answer(
        "Напишите одним сообщением ваш отзыв (только текст). "
        "Чтобы отменить, отправьте «Отмена».", reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [KeyboardButton(text="Отмена")]
            ],
        )
    )
    await callback.answer()


@router.message(ReviewSG.waiting_text, F.text)
async def review_receive(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get("_lock"):
        return
    await state.update_data(_lock=True)

    text = (message.text or "").strip()
    if text.lower() == "отмена":
        await state.clear()
        await message.answer("Отменено.")
        await _send_pending_lesson_if_any(message, state)
        return

    if not text:
        await message.answer("Пожалуйста, отправьте отзыв текстом.")
        await state.update_data(_lock=False)
        return

    if len(text) > 1000:
        await message.answer("Слишком длинно. Сократите до 1000 символов.")
        await state.update_data(_lock=False)
        return

    await send_message_safely(chat_id=REVIEW_CHAT_ID,
                              text=f"Новый отзыв от @{message.from_user.username or 'пользователя'}\n\n{text}")

    await message.answer("Спасибо! Ваш отзыв отправлен 🙌")
    await state.clear()
    await _send_pending_lesson_if_any(message, state)


@router.callback_query(F.data == "feedback_cancel")
async def feedback_cancel_handle(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Отзыв не был оставлен")
    await callback.answer()


@router.callback_query(F.data == "feedback_skip")
async def feedback_skip_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Пропускаем отзыв.")
    await _send_pending_lesson_if_any(callback, state)
    await callback.answer()
