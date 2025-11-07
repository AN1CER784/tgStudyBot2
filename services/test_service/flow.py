# services/tests/flow.py
import logging
from typing import List, Optional, Tuple

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.crud.tests import get_test_by_attempt, get_answers_by_attempt
from database.crud.user import create_or_update_user_stage
from database.models import QType
from keyboards.user_keyboards import build_options_kb, continue_keyboard
from renderers.test_renderer import render_question_block, render_test_results, render_user_attempt
from services.checkout_user import check_user_stage
from services.curator_check_service import get_attempt
from services.notify_service import notify_curators_about_test_completion
from services.profile_service import show_profile
from services.test_service.engine import (
    start_test, get_question_payload, answer_single, answer_text,
    complete as _complete, parse_answer_cb
)
from utils.edit_message import update_host_message

logger = logging.getLogger(__name__)


# --- Универсальный старт потока теста ---

async def start_test_flow(
        callback: CallbackQuery,
        state: FSMContext,
        test_id: int,
        stage: str,
        state_cls,
        prefix: str
):
    await callback.answer()
    user_id = callback.from_user.id
    check_stage = await check_user_stage(user_id=user_id, stage=stage)
    if not check_stage:
        logger.info(f"User {callback.from_user.id} tried to start {stage} but not allowed")
        await callback.message.answer("Этот этап вам недоступен.\nВведите /continue чтобы продолжить")
        return
    allowed, *_ = check_stage
    if not allowed:
        logger.info(f"User {callback.from_user.id} tried to start {stage} but already completed")
        await callback.message.answer("Этот тест уже пройден.")
        await show_profile(callback.message, callback.from_user.id)
        return

    res = await start_test(user_id=user_id, test_id=test_id)
    if not res:
        await callback.message.answer("Тест сейчас недоступен.")
        return

    if res.description:
        await state.update_data(host_mid=callback.message.message_id)
        await update_host_message(callback.message, state, res.description)

    await state.set_state(state_cls.answering)
    await state.update_data(
        attempt_id=res.attempt_id,
        test_id=res.test_id,
        q_ids=res.q_ids,
        pos=0,
        host_mid=None,
        stage=stage,
        prefix=prefix,
        user_id=user_id
    )
    logger.info(f"User {callback.from_user.id} started {stage}")
    await send_current_question(callback.message, state, prefix=prefix)


# --- Хелперы состояния/навигации ---

async def get_question_data(message: Message, state: FSMContext) -> Optional[Tuple[int, List[int], int]]:
    data = await state.get_data()
    q_ids: List[int] = data.get("q_ids")
    pos: int = data.get("pos")
    attempt_id: int = data.get("attempt_id")

    if not attempt_id:
        await message.answer("Что-то пошло не так. Введите /continue и попробуйте снова")
        await state.clear()
        return None

    if pos >= len(q_ids):
        await finish_test(message, state)
        return None
    return attempt_id, q_ids, pos


async def send_current_question(message: Message, state: FSMContext, prefix: str):
    qdata = await get_question_data(message=message, state=state)
    if not qdata:
        return
    attempt_id, q_ids, pos = qdata
    q, opts = await get_question_payload(q_ids[pos])
    text = render_question_block(q, opts, index=pos + 1, total=len(q_ids))

    if q.type == QType.single and opts:
        kb = build_options_kb(prefix, opts, attempt_id, q.id)
        await update_host_message(message, state, text, reply_markup=kb)
    else:
        await update_host_message(message, state, text, reply_markup=None)
    logger.info(f"User {message.from_user.id} sent question {q.id} - {q.text}")


# --- Ответ по кнопке single ---

async def make_single_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parsed = parse_answer_cb(callback.data)
    if not parsed:
        await callback.answer("Некорректные данные", show_alert=True)
        return
    _, attempt_id, q_id, opt_id = parsed

    data = await state.get_data()
    if data.get("attempt_id") != attempt_id:
        await callback.answer("Эта попытка уже не активна.", show_alert=True)
        return

    await answer_single(attempt_id=attempt_id, q_id=q_id, opt_id=opt_id)
    await state.update_data(pos=data.get("pos", 0) + 1)
    logger.info(f"User {callback.from_user.id} answered single on question {q_id} with option {opt_id}")


# --- Финализация теста ---

async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    attempt_id: int = data.get("attempt_id")
    current_stage = data.get("stage")
    user_id = data.get("user_id")
    percent, passed, score, max_score = await _complete(attempt_id)
    test = await get_test_by_attempt(attempt_id)
    text = render_test_results(test, passed, percent)

    stage_map = {"entry_test": "lesson", "final_test": "done"}
    next_stage = stage_map.get(current_stage) if passed else current_stage

    reply_markup = continue_keyboard(next_stage)
    if passed:
        logger.info(f"User {user_id} passed {current_stage} with {percent}%")
        await create_or_update_user_stage(
            user_id=user_id,
            stage=next_stage
        )
        if current_stage == "final_test":
            attempt = await get_attempt(attempt_id)
            if not attempt:
                logger.error(f"Attempt {attempt_id} not found")
                return
            answers = await get_answers_by_attempt(attempt.id)
            text_to_curator = render_user_attempt(attempt, answers)
            await notify_curators_about_test_completion(text_to_curator, attempt_id)
    else:
        logger.info(f"User {user_id} failed {current_stage} with {percent}%")

    await update_host_message(message, state, text, reply_markup=reply_markup)
    await state.clear()


# --- Текстовый ответ (если встретится text-вопрос) ---

async def make_text_answer_and_next(message: Message, state: FSMContext):
    qdata = await get_question_data(message, state)
    if not qdata:
        return
    attempt_id, q_ids, pos = qdata

    q, _ = await get_question_payload(q_ids[pos])
    if q.type == QType.single:
        return  # ждём кнопку

    await answer_text(attempt_id=attempt_id, q_id=q.id, text=message.text)
    await state.update_data(pos=pos + 1)
    await message.delete()
    await send_current_question(message, state, prefix=(await state.get_data()).get("prefix", "et"))
    logger.info(f"User {message.from_user.id} answered text on question {q.id} with text {message.text}")
