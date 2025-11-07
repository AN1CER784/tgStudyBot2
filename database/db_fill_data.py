from typing import Tuple

from tortoise.transactions import atomic

from constants.lessons_to_create import LESSONS
from constants.tests_to_create import DESCRIPTION_ET, MCQS_ET, LETTER_ORDER, MCQS_FT, DESCRIPTION_FT, \
    ENTRY_TEST_FAIL_MESSAGE, ENTRY_TEST_COMPLETION_MESSAGE, FINAL_TEST_FAIL_MESSAGE, \
    FINAL_TEST_NORMAL_COMPLETION_MESSAGE
from database.models import Test, Question, QType, Option, Lesson


@atomic()
async def seed_final_test(shuffle_questions: bool = False, single_points: float = 1.0) -> int:
    """
    Создаёт/обновляет «Финальное тестирование» и возвращает его ID.
    """
    test, created = await Test.update_or_create(

        title="Финальное тестирование",
        defaults={"description": DESCRIPTION_FT, "shuffle_questions": shuffle_questions, "fail_message": FINAL_TEST_FAIL_MESSAGE, "normal_success_message": FINAL_TEST_NORMAL_COMPLETION_MESSAGE, "perfect_success_message": FINAL_TEST_NORMAL_COMPLETION_MESSAGE},
    )
    if not created:
        # Полностью перезаливаем вопросы
        await Question.filter(test=test).delete()

    order = 1
    for q_text, variants, correct_letter in MCQS_FT:
        q = await Question.create(
            test=test,
            text=q_text,
            type=QType.single,
            order=order,
            points=single_points,
        )
        for letter, opt_text in variants:
            await Option.create(
                question=q,
                text=opt_text,
                is_correct=(letter == correct_letter),
                order=LETTER_ORDER.get(letter, 0),
            )
        order += 1

    return test.id


@atomic()
async def seed_entry_test(shuffle_questions: bool = False, single_points: float = 1.0) -> int:
    """
    Создаёт/обновляет вводный тест и возвращает его ID.
    """

    test, created = await Test.update_or_create(

        title="Вводное тестирование",
        defaults={"description": DESCRIPTION_ET, "shuffle_questions": shuffle_questions, "fail_message": ENTRY_TEST_FAIL_MESSAGE, "normal_success_message": ENTRY_TEST_COMPLETION_MESSAGE},
    )
    if not created:
        await test.save()
        # Удалим старые вопросы (опции удалятся каскадом)
        await Question.filter(test=test).delete()

    order = 1

    # Вопросы с вариантами (single)
    for q_text, variants, correct_letter in MCQS_ET:
        q = await Question.create(

            test=test,
            text=q_text,
            type=QType.single,
            order=order,
            points=single_points,
        )
        for letter, opt_text in variants:
            await Option.create(

                question=q,
                text=opt_text,
                is_correct=(letter == correct_letter),
                order=LETTER_ORDER.get(letter, 0),
            )
        order += 1

    return test.id


@atomic()
async def seed_lessons() -> Tuple[int, int]:
    """
    Создаёт/обновляет уроки. Возвращает кортеж: (created, updated).
    """
    created = 0
    updated = 0
    for item in LESSONS:
        obj, is_created = await Lesson.update_or_create(
            name=item["name"],
            defaults={
                "description": item.get("description", "")[:10000],
                "type": item["type"],
                "video_message_ids": item.get("video_message_ids", []),
                "response_type": item.get("response_type", "text"),
                "is_commentable": item.get("is_commentable", False),
            },
        )
        created += 1 if is_created else 0
        updated += 0 if is_created else 1
    return created, updated
