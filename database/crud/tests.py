import logging
from datetime import datetime
from typing import Iterable, List, Tuple

from tortoise.transactions import atomic

from constants.pagination import PAGE_SIZE
from database.models import Test, Question, Option, Attempt, Answer, QType
from database.models.test import AttemptStatus

logger = logging.getLogger(__name__)


async def get_test(test_id: int) -> Test | None:
    if test_id:
        return await Test.get_or_none(id=test_id)
    logger.warning("test_id is not set")


async def list_questions_for_test(test: Test) -> List[Question]:
    return await Question.filter(test=test).order_by("order").all()


async def list_options_for_question(q: Question) -> List[Option]:
    return await Option.filter(question=q).order_by("order").all()


async def compute_max_score(questions: Iterable[Question]) -> float:
    return sum(q.points for q in questions if q.type == QType.single)


async def create_attempt(user_id: int, test: Test, max_score: float) -> Attempt:
    prev_count = await Attempt.filter(user_id=user_id, test=test).count()
    return await Attempt.create(
        user_id=user_id, test=test, attempt_no=prev_count + 1, max_score=max_score
    )


async def list_attempts_final_unreviewed(page: int) -> Tuple[List[Attempt], int]:
    total = await Attempt.filter(review_comment__isnull=True).count()
    items = (
        await Attempt.filter(review_comment__isnull=True)
        .select_related("user")
        .order_by("id")
        .offset(page * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )

    return items, total


@atomic()
async def upsert_single_answer(
        attempt_id: int, question_id: int, option: Option, question_points: float
) -> None:
    is_correct = bool(option.is_correct)
    points = question_points if is_correct else 0.0

    await Answer.update_or_create(
        defaults={
            "selected_option_id": option.id,
            "text_answer": None,
            "is_correct": is_correct,
            "points_awarded": points,
        },
        attempt_id=attempt_id,
        question_id=question_id,
    )
    # можно копить score на лету — дешёво и прозрачно
    total = sum(a.points_awarded for a in await Answer.filter(attempt_id=attempt_id))
    await Attempt.filter(id=attempt_id).update(score=total)


async def upsert_text_answer(
        attempt_id: int, question_id: int, text: str | None
) -> None:
    # текстовый: не идёт в статистику
    await Answer.update_or_create(
        defaults={"text_answer": text or "", "is_correct": None, "points_awarded": 0.0, "selected_option": None},
        attempt_id=attempt_id,
        question_id=question_id,
    )


async def finish_attempt(attempt_id: int) -> Tuple[float, float]:
    """Возвращает (score, max_score)."""
    att = await Attempt.get(id=attempt_id)
    answers = await Answer.filter(attempt=att).all()
    score = sum(a.points_awarded for a in answers)
    max_score = att.max_score or 0.0

    await Attempt.filter(id=attempt_id).update(
        score=score,
        finished_at=datetime.utcnow(),
        status=AttemptStatus.completed,
    )
    return score, max_score


async def get_question_with_options(q_id: int) -> Tuple[Question, List[Option]]:
    q = await Question.get(id=q_id)
    opts = await Option.filter(question=q).order_by("order").all()
    return q, opts


async def get_option_for_question(q: Question, option_id: int) -> Option:
    return await Option.get(id=option_id, question=q)


async def get_test_by_attempt(attempt_id: int) -> Test:
    attempt = await Attempt.get(id=attempt_id)
    return await Test.get(id=attempt.test_id)


async def get_questions_by_test(test_id: int) -> List[Question]:
    return await Question.filter(test_id=test_id).order_by("order").all()


async def get_answers_by_attempt(attempt_id: int) -> List[Answer]:
    return await Answer.filter(attempt_id=attempt_id).all().select_related("selected_option")
