from typing import List, Tuple

from tortoise.exceptions import IntegrityError, TransactionManagementError
from tortoise.transactions import atomic, in_transaction

from constants.pagination import PAGE_SIZE
from database.models import UserProgress, Lesson, LessonResponse, Attempt
from database.models.lesson import LessonResponseFile


async def ensure_stage_totals(progress: UserProgress) -> None:
    """Если не задано общее число уроков — считаем их и сохраняем."""
    if not progress.stage_total or progress.stage_total <= 0:
        total = await Lesson.all().count()
        progress.stage_total = total  # даже если 0 — это явное значение
        await progress.save()


async def update_or_create_response(
        lesson_id: int,
        user_id: int,
        text: str,
) -> tuple["LessonResponse", bool]:
    """
    Обновляет ответ только если он был отклонён (is_correct=False).
    Если записи нет — создаёт.
    Возвращает (obj, created).
    """

    async with in_transaction():
        # 1) Пытаемся ОБНОВИТЬ ТОЛЬКО отклонённый ответ
        updated = await LessonResponse.filter(
            user_id=user_id,
            lesson_id=lesson_id,
            is_correct=False,
        ).update(
            response=text or "",
            is_correct=None,  # сбрасываем на "ожидает проверки"
        )

        if updated:
            obj = await LessonResponse.get(user_id=user_id, lesson_id=lesson_id)
            return obj, False  # обновили существующий

        # 2) Если не обновили — проверим, существует ли вообще ответ
        existing = await LessonResponse.get_or_none(user_id=user_id, lesson_id=lesson_id)
        if existing:
            return existing, None  # есть, но не отклонён -> не трогаем

        # 3) Иначе создаём новый (может упасть на гонке — ловим)
        try:
            obj = await LessonResponse.create(
                user_id=user_id,
                lesson_id=lesson_id,
                response=text or "",
                is_correct=None,
            )
            return obj, True
        except (IntegrityError, TransactionManagementError):
            # кто-то создал параллельно — просто вернём существующий
            obj = await LessonResponse.get(user_id=user_id, lesson_id=lesson_id)
            return obj, None


async def create_response_attachment(response_id: int, file_type: str, file_id: str) -> tuple[
    LessonResponse, bool]:
    """Создаёт приложение к ответу."""
    return await LessonResponseFile.create(
        lesson_response_id=response_id,
        file_type=file_type,
        file_id=file_id or "",
    )


async def get_attachments_by_response(response_id: int) -> List[LessonResponseFile]:
    """Получаем прикрепленные файлы к ответу на урок"""
    return await LessonResponseFile.filter(lesson_response_id=response_id).all()


async def get_current_lesson(progress: UserProgress) -> Lesson | None:
    """Берём текущий урок по stage_index (1-based)."""
    await ensure_stage_totals(progress)
    total = progress.stage_total or 0
    if total == 0:
        return None

    idx = progress.stage_index or 1
    # не даём уйти за пределы
    if idx < 1 or idx > total:
        return None

    lessons: List[Lesson] = (
        await Lesson.all()
        .order_by("id")
        .offset(idx - 1)
        .limit(1)
    )
    return lessons[0] if lessons else None


async def advance_to_next_lesson(progress: UserProgress) -> None:
    """Сдвигает индекс на следующий урок"""
    progress.stage_index = (progress.stage_index or 1) + 1
    if progress.stage_index > progress.stage_total:
        UserProgress.current_stage = "final_test"
    await progress.save()


async def list_pending(page: int) -> Tuple[List[LessonResponse], int]:
    total = await LessonResponse.filter(is_correct__isnull=True).count()
    items = (
        await LessonResponse.filter(is_correct__isnull=True)
        .select_related("lesson", "user")  # FK → select_related
        .order_by("id")
        .offset(page * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )

    return items, total


async def get_response(resp_id: int) -> LessonResponse | None:
    return await LessonResponse.get_or_none(id=resp_id).select_related("lesson", "user")


async def get_unchecked_response_by_user_and_lesson(user_id: int, lesson_id: int) -> LessonResponse | None:
    return await LessonResponse.get_or_none(user_id=user_id, lesson_id=lesson_id, is_correct=None).select_related(
        "lesson", "user")


@atomic()
async def accept_response(resp: LessonResponse) -> None:
    resp.is_correct = True
    await resp.save()
    user_progress = await UserProgress.get_or_none(user=resp.user)
    lesson_index = resp.lesson.id
    if user_progress:
        user_progress.stage_index = lesson_index + 1
        user_progress.current_stage = "lesson"
        await user_progress.save()


@atomic()
async def reject_response(resp: LessonResponse) -> None:
    resp.is_correct = False
    await resp.save()
    user_progress = await UserProgress.get_or_none(user=resp.user)
    lesson_index = resp.lesson.id
    if user_progress:
        user_progress.stage_index = lesson_index
        user_progress.current_stage = "lesson"
        await user_progress.save()


async def get_attempt_by_id(attempt_id: int) -> Attempt | None:
    return await Attempt.filter(id=attempt_id).first().select_related("user")
