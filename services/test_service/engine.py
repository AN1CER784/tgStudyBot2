import random
from typing import List, Tuple, Optional

from database.crud import (
    list_questions_for_test, compute_max_score, create_attempt,
    get_question_with_options, get_option_for_question,
    upsert_single_answer, upsert_text_answer, finish_attempt, get_test
)
from database.models import Question, Option
from services.test_service.dto import StartResult


# --- Старт попытки ---

async def start_test(user_id: int, test_id: int) -> StartResult | None:
    test = await get_test(test_id=test_id)
    if not test:
        return None

    questions = await list_questions_for_test(test)
    if not questions:
        return None

    if test.shuffle_questions:
        random.shuffle(questions)

    max_score = await compute_max_score(questions)
    attempt = await create_attempt(user_id=user_id, test=test, max_score=max_score)
    description = test.description or ""
    return StartResult(
        attempt_id=attempt.id,
        test_id=test.id,
        q_ids=[q.id for q in questions],
        description=description,
    )


# --- Добыча данных вопроса/опций для UI ---

async def get_question_payload(q_id: int) -> Tuple[Question, List[Option]]:
    return await get_question_with_options(q_id)


# --- Сохранение ответов ---

async def answer_single(attempt_id: int, q_id: int, opt_id: int) -> None:
    q, _ = await get_question_with_options(q_id)
    opt = await get_option_for_question(q, opt_id)
    await upsert_single_answer(
        attempt_id=attempt_id,
        question_id=q.id,
        option=opt,
        question_points=q.points
    )


async def answer_text(attempt_id: int, q_id: int, text: str | None) -> None:
    await upsert_text_answer(attempt_id=attempt_id, question_id=q_id, text=text)


# --- Подсчёт результата ---

async def complete(attempt_id: int) -> tuple[int, bool, float, float]:
    score, max_score = await finish_attempt(attempt_id)
    percent = 0 if max_score <= 0 else round(score / max_score * 100)
    passed = percent >= 50
    return percent, passed, score, max_score


# --- Разбор callback-data ---

def parse_answer_cb(data: str) -> Optional[tuple[str, int, int, int]]:
    """
    Ждём: "{prefix}:ans:{attempt_id}:{q_id}:{opt_id}"
    -> (prefix, attempt_id, q_id, opt_id)
    """
    try:
        prefix, ans, attempt_id, q_id, opt_id = data.split(":")
        if ans != "ans":
            return None
        return prefix, int(attempt_id), int(q_id), int(opt_id)
    except Exception:
        return None
