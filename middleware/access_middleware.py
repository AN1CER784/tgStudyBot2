from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from commands.set_commands import set_commands
from config import ADMINS
from database.crud import add_or_update_user
from database.crud.user import get_user


class AccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user_id = (event.from_user.id if isinstance(event, (Message, CallbackQuery)) and event.from_user else None)
        user = await get_user(user_id=user_id)
        if user:
            if user.is_allowed:
                return await handler(event, data)
        if user_id in ADMINS:
            await add_or_update_user(user_id=user_id, role="admin", is_allowed=True)
            return await handler(event, data)
        else:
            if isinstance(event, Message):
                await event.answer("Доступ к боту ограничен. Обратитесь к администратору.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Доступ к боту ограничен. Обратитесь к администратору.", show_alert=True)
            return
