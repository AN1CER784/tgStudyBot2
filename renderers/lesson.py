from database.models import Lesson, User
from database.models.lesson import LessonType


def lesson_renderer(lesson: Lesson):
    header = f"<b>{lesson.name}</b>\nТип: {'Урок с заданием' if lesson.type == LessonType.task_lesson else 'Урок'}"
    body = (lesson.description or "").strip()
    text = f"{header}\n\n{body}".strip()
    return text


def lesson_response_renderer(user: User, lesson: Lesson, response_text: str):
    lesson_response_text = (
        f"📝 <b>Ответ на проверку</b>\n"
        f"Пользователь: <code>{user.full_name}</code>\n"
        f"Урок: <b>{lesson.name}</b>\n\n"
    )
    lesson_response_text += (
         f"<i>Текст ответа:</i>\n{response_text or ''}" if lesson.response_type == "text" else ''
    )
    return lesson_response_text


def lesson_response_checked_renderer(passed: bool, lesson: Lesson, response_text: str, review_comment: str):
    lesson_response_checked_text = (
        f"✅ <b>Ответ принят</b>\n" if passed else f"❌ <b>Ответ не принят</b>\n"
    )
    lesson_response_checked_text += (
        f"Урок: <b>{lesson.name}</b>\n\n"
        f"<i>Текст ответа:</i>\n{response_text or ''}\n\n"
        f"<i>Комментарий куратора:</i>\n\n{review_comment or ''}"
    )
    lesson_response_checked_text += f"\n\nНаберите /continue, чтобы получить следующий урок." if passed else "\n\nНаберите /continue, чтобы снова увидеть задание"
    return lesson_response_checked_text
