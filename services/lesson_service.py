import logging

from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import bot, GROUP_CHAT_ID
from database.crud.lesson import advance_to_next_lesson
from database.models import Lesson, UserProgress
from database.models.lesson import LessonType
from keyboards.user_keyboards import continue_keyboard
from renderers.lesson import lesson_renderer
from states.lesson import LessonAnswerSG

logger = logging.getLogger(__name__)


async def send_lesson(message: Message, lesson: Lesson, progress: UserProgress, state: FSMContext):
    """
    Отправляет текущий урок.
    - free_lesson: показываем и сразу двигаем прогресс на следующий.
    - task_lesson: просим прислать текстовый ответ, ставим FSM ожидания.
    """
    text = lesson_renderer(lesson)
    logger.info(f"Sending lesson {lesson.id} - {lesson.type} - {lesson.name} to user {message.from_user.id}")
    msg_ids = lesson.video_message_ids
    for msg_id in msg_ids:
        await send_video_by_video_msg_id(video_msg_id=msg_id, chat_id=message.chat.id)
    if lesson.type == LessonType.free_lesson:
        await message.answer(text, reply_markup=continue_keyboard("lesson", "➡️ Запросить следующий урок"))
        # free_lesson сразу считаем пройденным
        await advance_to_next_lesson(progress)
    else:
        # task_lesson — ждём письменный ответ
        if lesson.response_type == "file":
            await message.answer(f"{text}\n\nОтправьте ответ в виде файла.",)
        else:
            await message.answer(f"{text}\n\nОтправьте письменный ответ одним сообщением.", )
        await state.set_state(LessonAnswerSG.waiting)
        await state.update_data(current_lesson_id=lesson.id)


async def send_video_by_video_msg_id(video_msg_id: int, chat_id: int):
    """
    Отправляет видео по video_msg_id
    """
    try:
        await bot.forward_message(chat_id=chat_id, from_chat_id=GROUP_CHAT_ID, message_id=int(video_msg_id))
    except TelegramAPIError:
        logger.error(f"Video message {video_msg_id} not found")
