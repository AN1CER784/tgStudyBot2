from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import bot
from constants.callbacks import CUR_OPEN_PREFIX, CUR_OK_PREFIX, CUR_REJECT_PREFIX, CURATOR_MENU, CUR_OPEN_FINAL_PREFIX, \
    CUR_COMMENT_FINAL_PREFIX
from constants.on_going_messages import ON_DONE_MESSAGE
from database.crud.lesson import accept_response, reject_response, get_response, get_attempt_by_id, \
    get_attachments_by_response
from database.crud.tests import get_answers_by_attempt
from keyboards.curator_keyboards import curator_detail_kb, curator_final_comment_kb
from renderers.lesson import lesson_response_renderer, lesson_response_checked_renderer
from renderers.test_renderer import render_user_attempt
from services.curator_check_service import response_checkout, attempt_checkout
from services.notify_service import notify_user_about_submission
from states.curator import CuratorCommentLessonSG, CuratorCommentFinalSG
from utils.back_kb import back_button

router = Router(name="review_router")


@router.callback_query(F.data.startswith(f"{CUR_OPEN_FINAL_PREFIX}:"))
async def cb_open_final_user(callback: CallbackQuery):
    attempt = await attempt_checkout(callback)
    if not attempt:
        return
    answers = await get_answers_by_attempt(attempt.id)
    text = render_user_attempt(attempt, answers)
    await callback.message.answer(text, reply_markup=curator_final_comment_kb(attempt.id), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith(f"{CUR_COMMENT_FINAL_PREFIX}:"))
async def cb_open_final_comment(callback: CallbackQuery, state: FSMContext):
    attempt = await attempt_checkout(callback)
    if not attempt:
        return
    await state.set_state(CuratorCommentFinalSG.waiting)
    await state.update_data(attempt_id=attempt.id)
    await callback.message.edit_text(
        f"✍️ Напишите комментарий для пользователя по прохождению курса.",
        parse_mode="HTML", reply_markup=back_button(prefix=CURATOR_MENU)
    )
    await callback.answer()


@router.message(CuratorCommentFinalSG.waiting)
async def final_user_message_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    attempt_id: int = data.get("attempt_id")
    comment = (message.text or "").strip()
    if not comment:
        await message.answer("Комментарий пустой. Пожалуйста, напишите текст комментария.",
                             reply_markup=back_button(CURATOR_MENU))
        return
    attempt = await get_attempt_by_id(attempt_id)
    if not attempt:
        await message.answer("Попытка не найдена. Пожалуйста, попробуйте ещё раз.",
                             reply_markup=back_button(CURATOR_MENU))
        return
    attempt.review_comment = comment
    await attempt.save()

    appeal_to_user = "Дорогая " if attempt.user.sex == "woman" else "Дорогой " + attempt.user.full_name
    await notify_user_about_submission(user_id=attempt.user.id,
                                       message_text=f"{appeal_to_user}, {ON_DONE_MESSAGE}")
    await notify_user_about_submission(user_id=attempt.user.id,
                                       message_text=f"Комментарий куратора по обучению:\n\n{comment}")
    await message.answer("Комментарий отправлен.", reply_markup=back_button(CURATOR_MENU))
    await state.clear()


@router.callback_query(F.data.startswith(f"{CUR_OPEN_PREFIX}:"))
async def cb_open_lesson_response(callback: CallbackQuery):
    lesson_response = await response_checkout(callback)
    if not lesson_response:
        return
    text = lesson_response_renderer(lesson_response.user, lesson_response.lesson, lesson_response.response)
    if lesson_response.lesson.response_type == "file":
        attachments = await get_attachments_by_response(lesson_response.id)
        for attachment in attachments:
            if attachment.file_type == "photo":
                await callback.message.answer_photo(
                    attachment.file_id,  # ← просто file_id строкой
                )
            elif attachment.file_type == "video":
                await callback.message.answer_video(
                    attachment.file_id,  # ← просто file_id строкой
                )
            elif attachment.file_type == "document":
                await callback.message.answer_document(
                    attachment.file_id,  # ← просто file_id строкой
                )
            else:
                await callback.message.answer("Неизвестный тип файла")
    await callback.message.answer(text, reply_markup=curator_detail_kb(lesson_response.id), parse_mode="HTML")
    await callback.answer()


# --- Принять: просим комментарий ---
@router.callback_query(F.data.startswith(f"{CUR_OK_PREFIX}:"))
async def cb_lesson_response_ok(callback: CallbackQuery, state: FSMContext):
    lesson_response = await response_checkout(callback)
    if not lesson_response:
        return
    await callback.message.delete()
    await state.set_state(CuratorCommentLessonSG.waiting)
    await state.update_data(decision="ok", lesson_response_id=lesson_response.id)
    await callback.message.answer(
        f"✍️ Напишите комментарий для пользователя по ответу #{lesson_response.id} "
        f"на урок {lesson_response.lesson.name}",
        parse_mode="HTML", reply_markup=back_button(prefix=CURATOR_MENU)
    )
    await callback.answer()


# --- Отклонить: просим комментарий ---
@router.callback_query(F.data.startswith(f"{CUR_REJECT_PREFIX}:"))
async def cb_lesson_response_reject(callback: CallbackQuery, state: FSMContext):
    lesson_response = await response_checkout(callback)
    if not lesson_response:
        return
    await callback.message.delete()
    await state.set_state(CuratorCommentLessonSG.waiting)
    await state.update_data(decision="reject", lesson_response_id=lesson_response.id)
    await callback.message.answer(
        f"✍️ Напишите причину/рекомендации для пользователя по ответу #{lesson_response.id} "
        f"на урок {lesson_response.lesson.name}",
        parse_mode="HTML", reply_markup=back_button(prefix=CURATOR_MENU)
    )
    await callback.answer()


@router.message(CuratorCommentLessonSG.waiting)
async def lesson_response_message_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    decision = data.get("decision")
    lesson_response_id = data.get("lesson_response_id")

    comment = (message.text or "").strip()
    if not comment:
        await message.answer("Комментарий пустой. Пожалуйста, напишите текст комментария.",
                             reply_markup=back_button(CURATOR_MENU))
        return

    lesson_response = await get_response(lesson_response_id)
    if not lesson_response:
        await message.answer("Ответ не найден. Попробуйте еще раз.", reply_markup=back_button(prefix=CURATOR_MENU))
        return
    lesson_response.review_comment = comment
    if decision == "ok":
        await accept_response(lesson_response)
        checked_response_text = lesson_response_checked_renderer(passed=True, lesson=lesson_response.lesson,
                                                                 response_text=lesson_response.response,
                                                                 review_comment=comment)
        await message.answer("Принято ✅ Комментарий отправлен пользователю.")
    elif decision == "reject":
        await reject_response(lesson_response)
        checked_response_text = lesson_response_checked_renderer(passed=False, lesson=lesson_response.lesson,
                                                                 response_text=lesson_response.response,
                                                                 review_comment=comment)
        await message.answer("Отклонено ❌ Комментарий отправлен пользователю.")
    else:
        await message.answer("Что-то пошло не так. Попробуйте еще раз.", reply_markup=back_button(prefix=CURATOR_MENU))
        return
    await notify_user_about_submission(user_id=lesson_response.user.id,
                                       message_text=checked_response_text)
    await message.answer("Вернуться", reply_markup=back_button(prefix=CURATOR_MENU))
