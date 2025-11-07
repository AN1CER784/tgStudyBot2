from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import ADMINS
from database.crud import add_or_update_user
from database.models.user import User


class RoleGuard(BaseMiddleware):
    def __init__(self, allowed_roles: set[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]
                       ):
        user_id = (event.from_user.id if isinstance(event, (Message, CallbackQuery)) and event.from_user else None)
        if user_id is None:
            return

        user = await User.get_or_none(id=user_id)
        role = user.role if user else "user"
        if role in self.allowed_roles:
            return await handler(event, data)
        else:
            if user_id in ADMINS:
                await add_or_update_user(user_id=user_id, role="admin", is_allowed=True)
                return await handler(event, data)

        if isinstance(event, Message):
            await event.answer("Нет прав для этого раздела.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Недостаточно прав", show_alert=True)
        return
