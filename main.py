import asyncio
import logging

from aiogram import Dispatcher
from tortoise.exceptions import DBConnectionError

from commands.set_commands import set_commands
from config import bot
from database.database import close_db, init_db
from database.db_fill_data import seed_entry_test, seed_final_test, seed_lessons
from middleware.access_middleware import AccessMiddleware
from middleware.role_guard import RoleGuard
from routers import get_user_router, get_admin_router, get_curator_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%y %I:%M:%S', )

dp = Dispatcher(bot=bot)


async def on_startup():
    """
    Функция, которая будет выполняться при запуске бота.
    """
    try:
        await init_db()
        await seed_entry_test()
        await seed_final_test()
        await seed_lessons()
        await set_commands("user")
        logging.info("Бот запущен!")
    except DBConnectionError as e:
        logging.error(f"Ошибка при подключении к базе данных: {e}")
        raise


async def on_shutdown():
    """
    Функция, которая будет выполняться при остановке бота.
    """

    await close_db()
    logging.info("Бот остановлен!")


async def main():
    """
    Мейн функция запуска бота.
    Добавляем роутеры в диспетчера, регистрируем миддлвари и начинаем проверять обновления.
    """
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    logging.info(await bot.get_me())

    user_router = get_user_router()
    admin_router = get_admin_router()

    curator_router = get_curator_router()

    dp.include_routers(
        user_router,
        admin_router,
        curator_router
    )

    # подключаем middleware

    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

    admin_router.message.middleware(RoleGuard({"admin"}))
    admin_router.callback_query.middleware(RoleGuard({"admin"}))

    curator_router.message.middleware(RoleGuard({"admin", "curator"}))
    curator_router.callback_query.middleware(RoleGuard({"admin", "curator"}))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
