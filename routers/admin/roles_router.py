from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from constants.callbacks import ROLES_SET_PREFIX, ROLES_LIST_PREFIX, ROLES_CHANGE_PREFIX, REQ_CUR, REQ_ADMIN, \
    ROLES_MENU, ADMIN_MAIN
from database.crud.user import set_role, get_all_users
from keyboards.admin_keyboards import roles_item_row, pager_rows, request_user_kb, roles_menu_kb, role_change_kb
from services.admin_service import admin_checkout
from states.admin import AdminPickUserSG
from utils.back_kb import back_button

router = Router(name="roles_router")


@router.callback_query(F.data == ROLES_MENU)
async def cb_roles_menu(callback: CallbackQuery):
    await callback.message.edit_text("🛡 Управление ролями:", reply_markup=roles_menu_kb())
    await callback.answer()


@router.callback_query(F.data == REQ_ADMIN)
async def cb_req_admin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminPickUserSG.grant_admin)
    await callback.message.answer("Выберите пользователя для АДМИНА:",
                                  reply_markup=request_user_kb(201, "👑 Выбрать пользователя"))
    await callback.answer()


@router.callback_query(F.data == REQ_CUR)
async def cb_req_curator(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminPickUserSG.grant_curator)

    await callback.message.answer("Выберите пользователя для КУРАТОРА:",
                                  reply_markup=request_user_kb(202, "🎓 Выбрать пользователя"))
    await callback.answer()


@router.message(F.user_shared, AdminPickUserSG.grant_admin)
async def on_user_shared_role(message: Message, state: FSMContext):
    user = await set_role(message.user_shared.user_id, "admin")
    await message.answer(f"✅ Назначен АДМИН: {user.id}", reply_markup=back_button(ADMIN_MAIN))
    await state.clear()


@router.message(F.user_shared, AdminPickUserSG.grant_curator)
async def on_user_shared_role(message: Message, state: FSMContext):
    checkout = admin_checkout(message, tg_to_change_id=message.user_shared.user_id, cur_user_id=message.from_user.id)
    if checkout:
        return
    user = await set_role(message.user_shared.user_id, "curator")
    await message.answer(f"✅ Назначен КУРАТОР: {user.id}", reply_markup=back_button(ADMIN_MAIN))
    await state.clear()


@router.callback_query(F.data.startswith(f"{ROLES_LIST_PREFIX}:"))
async def cb_roles_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[-1])
    users, total = await get_all_users(page)
    rows = [roles_item_row(u) for u in users]
    rows += pager_rows(ROLES_LIST_PREFIX, page, total)
    rows += [[InlineKeyboardButton(text="⬅️ Назад", callback_data=ROLES_MENU)]]
    await callback.message.edit_text("Роли пользователей:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith(f"{ROLES_CHANGE_PREFIX}:"))
async def cb_roles_change(callback: CallbackQuery):
    tg_id = int(callback.data.split(":")[-1])
    await callback.message.edit_reply_markup(reply_markup=role_change_kb(tg_id))
    await callback.answer()


@router.callback_query(F.data.startswith(f"{ROLES_SET_PREFIX}:"))
async def cb_roles_set(callback: CallbackQuery):
    _, _, _, tg_id_str, role, _ = callback.data.split(":")
    checkout = await admin_checkout(callback.message, cur_user_id=callback.from_user.id, tg_to_change_id=int(tg_id_str))
    if checkout:
        return
    user = await set_role(int(tg_id_str), role)
    await callback.answer(f"Роль обновлена: {user.id} -> {user.role}")
