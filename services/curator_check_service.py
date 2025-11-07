from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from constants.callbacks import CURATOR_MENU, CUR_LIST_PREFIX, CUR_OPEN_PREFIX, CUR_LIST_FINAL_PREFIX, \
    CUR_OPEN_FINAL_PREFIX
from database.crud.lesson import list_pending, get_response
from database.crud.tests import list_attempts_final_unreviewed, get_answers_by_attempt
from database.models import LessonResponse, Attempt
from keyboards.curator_keyboards import curator_list_kb
from renderers.lesson import lesson_response_renderer
from renderers.test_renderer import render_user_attempt
from utils.back_kb import back_button


async def send_list(target_message: Message, page: int,
                    list_type: type[LessonResponse] | type[Attempt] = LessonResponse) -> None:
    items, total = await list_pending(page) if list_type == LessonResponse else await list_attempts_final_unreviewed(
        page)
    if not items:
        await target_message.edit_text("Нет ответов, ожидающих проверки.",
                                       reply_markup=back_button(CURATOR_MENU))
        return
    callback_list, callback_row = (CUR_LIST_PREFIX, CUR_OPEN_PREFIX) if list_type == LessonResponse else (
        CUR_LIST_FINAL_PREFIX, CUR_OPEN_FINAL_PREFIX)
    await target_message.edit_text("⏳ Ответы на проверке:",
                                   reply_markup=curator_list_kb(items, page, total, callback_list=callback_list,
                                                                callback_row=callback_row))


async def response_checkout(callback: CallbackQuery) -> LessonResponse | None:
    resp_id = int(callback.data.split(":")[-1])
    lesson_response = await get_response(resp_id)
    if not lesson_response:
        await callback.answer("Ответ не найден", show_alert=True)
        return
    if lesson_response.is_correct is not None:
        await callback.answer("Ответ уже проверен", show_alert=True)
        return
    return lesson_response


async def attempt_checkout(callback: CallbackQuery) -> Attempt | None:
    attempt_id = int(callback.data.split(":")[-1])
    attempt = await get_attempt(attempt_id)
    if not attempt:
        await callback.answer("Попытка не найдена", show_alert=True)
        return
    return attempt


async def get_attempt(attempt_id: int) -> Attempt | None:
    return await Attempt.get(id=attempt_id).select_related("user", "test").prefetch_related("test__questions",
                                                                                            "test__questions__options")


async def get_lesson_or_test_response(callback: CallbackQuery):
    """
    Общая функция для получения ответа урока или теста.
    """
    if callback.data.startswith(CUR_OPEN_PREFIX):
        lesson_response = await response_checkout(callback)
        if not lesson_response:
            return None, "Урок не найден."
        return lesson_response, lesson_response_renderer(lesson_response.user, lesson_response.lesson,
                                                         lesson_response.response)
    elif callback.data.startswith(CUR_OPEN_FINAL_PREFIX):
        attempt = await attempt_checkout(callback)
        if not attempt:
            return None, "Попытка не найдена."
        answers = await get_answers_by_attempt(attempt.id)
        return attempt, render_user_attempt(attempt, answers)
    return None, "Ответ не найден."


async def ask_for_comment(callback: CallbackQuery, state: FSMContext, state_cls, prompt: str):
    """
    Универсальный обработчик для запроса комментариев.
    """
    # Получаем ответ
    response, render_text = await get_lesson_or_test_response(callback)
    if not response:
        await callback.answer(render_text, show_alert=True)
        return

    await state.set_state(state_cls.waiting)
    await state.update_data(response_id=response.id)
    await callback.message.edit_text(prompt, parse_mode="HTML", reply_markup=back_button(prefix=CURATOR_MENU))
    await callback.answer()
