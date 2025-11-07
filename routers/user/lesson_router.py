import logging
from typing import Optional, Dict, Any, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from tortoise.transactions import in_transaction

from constants.on_going_messages import LESSONS_COMPLETE_MESSAGE
from database.crud.lesson import create_response_attachment, update_or_create_response, get_attachments_by_response
from database.crud.lesson import get_current_lesson
from database.crud.user import create_or_update_user_stage
from keyboards.user_keyboards import continue_keyboard, attachments_kb, feedback_prompt_kb
from services.checkout_user import check_user_stage
from services.lesson_response_service import finalize_submission, _reply, load_ctx
from services.lesson_service import send_lesson
from states.lesson import LessonAnswerSG
from utils.handle_file import handle_file_from_message

logger = logging.getLogger(__name__)

router = Router(name="lesson_router")


async def add_pending_attachment(
        state: FSMContext,
        *,
        file_id: str,
        file_type: str,
        file_unique_id: Optional[str] = None,
) -> bool:
    """
    Кладёт вложение в FSM. Возвращает False, если такой unique_id уже добавляли.
    """
    data = await state.get_data()
    items: List[Dict[str, Any]] = data.get("pending_attachments") or []

    if file_unique_id and any(it.get("file_unique_id") == file_unique_id for it in items):
        return False

    items.append({
        "file_id": file_id,
        "file_type": file_type,
        "file_unique_id": file_unique_id,
    })
    await state.update_data(pending_attachments=items)
    return True


@router.callback_query(F.data == "continue:lesson")
async def lesson_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    checkout = await check_user_stage(callback.from_user.id, "lesson")
    if not checkout:
        logger.info(f"User {callback.from_user.id} is not allowed to start lesson")
        await callback.message.answer("Этот этап вам недоступен.\nВведите /continue чтобы продолжить")
        return
    checkout_stage, progress = checkout
    lesson = await get_current_lesson(progress)
    if not lesson:
        logger.info(f"User {callback.from_user.id} has no current lesson, final test suggested")
        await create_or_update_user_stage(user_id=callback.from_user.id, stage="final_test")
        await callback.message.answer(f"🎉 Все уроки пройдены! {LESSONS_COMPLETE_MESSAGE}",
                                      reply_markup=continue_keyboard('final_test', "🟢 Начать итоговый тест"))
        return
    if lesson.is_commentable:
        await state.update_data(pending_lesson_id=lesson.id)
        await callback.message.answer(
            "Перед началом следующего урока оставите короткий отзыв? Это займёт минуту.",
            reply_markup=feedback_prompt_kb()
        )
        await callback.answer()
        return
    await send_lesson(callback.message, lesson, progress, state)
    await callback.answer()


@router.message(LessonAnswerSG.waiting, ~F.text)
async def on_file_part(message: Message, state: FSMContext):
    ctx = await load_ctx(message, state, expected_type="file")
    if not ctx:
        return

    file_id, file_type = handle_file_from_message(message)
    if not file_id:
        await _reply(message, "Неверный формат файла. Пришлите документ/фото/видео/аудио.")
        return

    ok = await add_pending_attachment(state, file_id=file_id, file_type=file_type)
    if not ok:
        await _reply(message, "Этот файл уже добавлен.")
        return

    data = await state.get_data()
    cnt = len(data.get("pending_attachments", []))
    await _reply(
        message,
        f"Файл прикреплён. Сейчас в ответе: {cnt} файлов\n"
        "Можете добавить ещё или отправить на проверку",
        reply_markup=attachments_kb()
    )


@router.callback_query(F.data == "attach_done")
async def cb_done(callback: CallbackQuery, state: FSMContext):
    ctx = await load_ctx(callback, state, expected_type="file")
    if not ctx:
        await callback.answer()
        return

    data = await state.get_data()
    pending = data.get("pending_attachments") or []
    if not pending:
        await callback.answer("Нечего отправлять.", show_alert=True)
        return
    async with in_transaction():
        lr, _created = await update_or_create_response(
            user_id=ctx.user.id, lesson_id=ctx.lesson_id, text="Ответ прикреплены файлом"
        )
        if not _created:
            attachments = await get_attachments_by_response(lr.id)
            for attachment in attachments:
                await attachment.delete()
        for item in pending:
            await create_response_attachment(
                response_id=lr.id, file_id=item["file_id"], file_type=item["file_type"]
            )
    await finalize_submission(callback, state, ctx, response_id=lr.id, response_text="Ответ в файле")
    await callback.answer()


@router.callback_query(F.data == "attach_cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await _reply(callback, "Отменено. Можете начать заново.")
    await callback.answer()


@router.message(LessonAnswerSG.waiting, F.text)
async def on_text_answer(message: Message, state: FSMContext):
    ctx = await load_ctx(message, state, expected_type="text")
    if not ctx:
        return

    text = (message.text or "").strip()
    if not text:
        await _reply(message, "Ответ должен быть текстом.")
        return
    if len(text) > 2000:
        await _reply(message, "Слишком длинный ответ. Сократите до 2000 символов.")
        return

    from database.crud.lesson import get_unchecked_response_by_user_and_lesson, update_or_create_response
    existing = await get_unchecked_response_by_user_and_lesson(user_id=ctx.user.id, lesson_id=ctx.lesson_id)

    lr, created = await update_or_create_response(
        user_id=ctx.user.id, lesson_id=ctx.lesson_id, text=text
    )
    if existing or created is None:
        await _reply(message, "Вы уже отправили ответ. Дождитесь проверки куратора.")
        await state.clear()
        return
    await finalize_submission(message, state, ctx, response_id=lr.id, response_text=text)


@router.callback_query(F.data == "continue:lesson_on_completion")
async def lesson_on_completion_handle(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    checkout_stage, progress = await check_user_stage(callback.from_user.id, "lesson_on_completion")
    if not checkout_stage:
        await callback.message.edit_text(
            "Этот этап вам недоступен.\nВведите /continue чтобы продолжить")
        return
    await callback.message.edit_text("Ваш ответ на проверке у куратора.\nДождитесь его ответа.")
    logger.info(f"User {callback.from_user.id} is on lesson on completion")
