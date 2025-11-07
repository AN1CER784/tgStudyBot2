from typing import Literal

from database.crud.lesson import get_current_lesson
from database.models import User, UserProgress
from database.models.user import Stage
from services.admin_service import get_role_match
from utils.get_human_sex import get_sex_human


def stage_human(stage: Stage) -> str:
    mapping = {
        Stage.start: "Не зарегистрирован",
        Stage.entry_test: "Входной тест",
        Stage.lesson: "Урок",
        Stage.lesson_on_completion: "Ответ на задание на проверке",
        Stage.final_test: "Итоговый тест",
        Stage.done: "Обучение завершено",
    }
    return mapping.get(stage, str(stage))


async def render_profile(user: User, progress: UserProgress | None = None, requested_by: Literal['user', 'staff'] = 'user') -> str:
    name = user.full_name or "—"
    dob = user.birthday.strftime("%d.%m.%Y") if user.birthday else "—"
    phone = user.phone or "—"
    sex = user.sex.value or "—"

    prog = "Нет данных"
    if progress:
        if progress.current_stage == Stage.lesson and (progress.stage_total or 0) > 0:
            pct = round((progress.stage_index / progress.stage_total) * 100)
            prog = f"{stage_human(progress.current_stage)} — задача {progress.stage_index}/{progress.stage_total} ({pct}%)"
        else:
            prog = stage_human(progress.current_stage)
    profile_text = "<b>Профиль</b>\n" \
                   f"Фамилия, имя: <b>{name}</b>\n" \
                   f"Дата рождения: <b>{dob}</b>\n" \
                   f"Телефон: <b>{phone}</b>\n" \
                   f"Пол: <b>{get_sex_human(sex)}</b>\n"

    if user.role == 'user':
        profile_text += f"Прогресс: <b>{prog}</b>"
        if progress:
            lesson = await get_current_lesson(progress)
            if progress.current_stage == Stage.lesson:
                profile_text += f" <b>{lesson.name}</b>\nВ процессе выполнения"
            elif progress.current_stage == Stage.lesson_on_completion:
                profile_text += f" <b>{lesson.name}</b>\nОжидание ответа куратора по уроку"

    if requested_by == 'user':
        profile_text += '\nЧтобы продолжить введите /continue'
        profile_text += "\n\nДля изменения информации о себе введите /edit"
    elif requested_by == 'staff':
        profile_text += f'\nДоступ к боту: ' + 'есть' if user.is_allowed else 'нет'
        profile_text += f'\nРоль: ' + get_role_match(user.role)
    return profile_text
