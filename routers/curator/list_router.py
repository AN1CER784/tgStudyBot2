from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from constants.callbacks import CURATOR_MENU, CUR_LIST_PREFIX, CUR_LIST_FINAL_PREFIX
from database.models import Attempt
from keyboards.curator_keyboards import curator_menu_kb
from services.admin_service import is_admin_user
from services.curator_check_service import send_list

router = Router(name="list_router")


@router.callback_query(F.data == CURATOR_MENU)
@router.callback_query(F.data == f"continue:{CURATOR_MENU}")
async def cb_curator_menu(callback: CallbackQuery, state: FSMContext):
    is_admin = await is_admin_user(callback.from_user.id)
    await callback.message.edit_text("Выберите действие:", reply_markup=curator_menu_kb(is_admin))
    await callback.answer()


@router.message(Command("curator"))
async def cmd_curator(message: Message):
    is_admin = await is_admin_user(message.from_user.id)
    await message.answer("Выберите действие:", reply_markup=curator_menu_kb(is_admin))


@router.callback_query(F.data == CUR_LIST_PREFIX)
async def cb_curator_lessons_list(callback: CallbackQuery, state: FSMContext):
    await send_list(callback.message, 0)
    await callback.answer()


@router.callback_query(F.data.startswith(f"{CUR_LIST_PREFIX}:"))
async def cb_cur_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[-1])
    await send_list(callback.message, page, )
    await callback.answer()


@router.callback_query(F.data == CUR_LIST_FINAL_PREFIX)
async def cb_curator_lessons_list(callback: CallbackQuery, state: FSMContext):
    await send_list(callback.message, 0, list_type=Attempt)
    await callback.answer()


@router.callback_query(F.data.startswith(f"{CUR_LIST_FINAL_PREFIX}:"))
async def cb_cur_final_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[-1])
    await send_list(callback.message, page, list_type=Attempt)
    await callback.answer()
