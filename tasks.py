import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from celery import shared_task

from config import TOKEN
from database.crud.user import get_common_users_with_progress
from database.database import close_db, init_db

logger = logging.getLogger(__name__)


async def _run_dispatch():
    await init_db()
    async with Bot(token=TOKEN) as bot:
        try:
            users, total = await get_common_users_with_progress()
            logger.info(f"Total users: {total}")
            async for user in users:
                if user.progress.updated_at.date() <= datetime.now().date() - timedelta(days=2):
                    await bot.send_message(user.id, "Привет! Напоминаем, что вы можете продолжить обучение.\nДля продолжения нажмите /continue")
                    logger.info(f"Sent message to {user.id}")
        finally:
            await close_db()


@shared_task(name="tasks.dispatch_daily_messages")
def dispatch_daily_messages():
    # запускаем асинхронную часть
    asyncio.run(_run_dispatch())
