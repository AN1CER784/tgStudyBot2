from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from constants.callbacks import ADMIN_MAIN
from keyboards.admin_keyboards import admin_menu_kb

router = Router(name="menu_router")


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer("Админ-панель:", reply_markup=admin_menu_kb())


@router.callback_query(F.data == ADMIN_MAIN)
@router.callback_query(F.data == f"continue:{ADMIN_MAIN}")
async def cb_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text("Админ-панель:", reply_markup=admin_menu_kb())
    await callback.answer()
