
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from constants.callbacks import ACCESS_MENU, REQ_GRANT, ACCESS_LIST_PREFIX, ACCESS_TOGGLE_PREFIX, ADMIN_MAIN
from database.crud.user import grant_access, revoke_access, get_all_users, get_user
from keyboards.admin_keyboards import access_menu_kb, request_user_kb, allowed_item_row, pager_rows
from services.admin_service import admin_checkout
from states.admin import AdminPickUserSG
from utils.back_kb import back_button

router = Router(name="access_router")


@router.callback_query(F.data == ACCESS_MENU)
async def cb_access_menu(callback: CallbackQuery):
    await callback.message.edit_text("👥 Доступ к боту:", reply_markup=access_menu_kb())
    await callback.answer()


@router.callback_query(F.data == REQ_GRANT)
async def cb_req_grant(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminPickUserSG.grant_access)
    await callback.message.delete()
    await callback.message.answer("Выберите пользователя:", reply_markup=request_user_kb(101, "👤 Выбрать пользователя"))
    await callback.answer()


@router.message(F.user_shared, AdminPickUserSG.grant_access)
async def on_user_shared_grant(message: Message, state: FSMContext):
    user = await get_user(message.user_shared.user_id)
    if user:
        await message.answer(f"✅ Доступ уже был выдан: {user.id}", reply_markup=back_button(ADMIN_MAIN))
        await state.clear()
        return
    user = await grant_access(message.user_shared.user_id)
    await message.answer(f"✅ Доступ выдан: {user.id}", reply_markup=back_button(ADMIN_MAIN))
    await state.clear()


@router.callback_query(F.data.startswith(f"{ACCESS_LIST_PREFIX}:"))
async def cb_access_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[-1])
    users, total = await get_all_users(page)
    rows = [allowed_item_row(u) for u in users]
    rows += pager_rows(ACCESS_LIST_PREFIX, page, total)
    await callback.message.edit_text("Пользователи с доступом:", reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                                                                   rows + [[
                                                                                                       InlineKeyboardButton(
                                                                                                           text="⬅️ Назад",
                                                                                                           callback_data=ACCESS_MENU)]]
                                                                                                   ))
    await callback.answer()


@router.callback_query(F.data.startswith(f"{ACCESS_TOGGLE_PREFIX}:"))
async def cb_access_toggle(callback: CallbackQuery):
    _, _, _, tg_id_str, have_str = callback.data.split(":")
    tg_id = int(tg_id_str)
    checkout = await admin_checkout(callback.message, tg_to_change_id=tg_id, cur_user_id=callback.from_user.id)
    if checkout:
        return
    have = have_str == "1"
    if have:
        await revoke_access(tg_id)
        await callback.answer("Доступ отозван")
    else:
        await grant_access(tg_id)
        await callback.answer("Доступ выдан")