import logging

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import bot

logger = logging.getLogger(__name__)


async def send_message_safely(chat_id: int, text: str, reply_markup=None):
    """Безопасная отправка сообщения с обработкой исключений."""
    try:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
        logger.info(f"Message successfully sent to user {chat_id}.")
    except TelegramForbiddenError:
        logger.warning(f"User {chat_id} blocked bot. Message wasn't sent.")
        # Удаление или пометка пользователя в базе данных (если необходимо)
        # db.mark_user_inactive(chat_id)  # Пример вызова функции для базы данных
    except TelegramBadRequest as e:
        logger.error(f"Error sending message to user {chat_id}: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error when sending message to user {chat_id}: {e}")
