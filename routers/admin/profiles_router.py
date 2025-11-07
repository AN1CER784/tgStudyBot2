from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from constants.callbacks import ADMIN_MAIN, PROFILES_LIST_PREFIX, USER_PROFILE_PREFIX
from database.crud.user import get_all_users, get_user
from keyboards.admin_keyboards import user_item_row, pager_rows
from renderers.profile_renderer import render_profile

router = Router(name="profiles_router")


@router.callback_query(F.data.startswith(f"{PROFILES_LIST_PREFIX}:"))
async def cb_profiles_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[-1])
    users, total = await get_all_users(page)
    rows = [user_item_row(u) for u in users]
    rows += pager_rows(PROFILES_LIST_PREFIX, page, total)
    await callback.message.edit_text("Пользователи с доступом:", reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                                                                   rows + [[
                                                                                                       InlineKeyboardButton(
                                                                                                           text="⬅️ Назад",
                                                                                                           callback_data=ADMIN_MAIN)]]
                                                                                                   ))
    await callback.answer()


@router.callback_query(F.data.startswith(f"{USER_PROFILE_PREFIX}:"))
async def cb_user_profile(callback: CallbackQuery):
    tg_id = int(callback.data.split(":")[-1])
    user = await get_user(tg_id)
    profile_text = await render_profile(user, user.progress, requested_by='staff')
    await callback.message.edit_text(profile_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                                                                   [[
                                                                                                       InlineKeyboardButton(
                                                                                                           text="⬅️ Назад",
                                                                                                           callback_data=PROFILES_LIST_PREFIX + ":0")]]

                                                                                                   ))
    await callback.answer()
