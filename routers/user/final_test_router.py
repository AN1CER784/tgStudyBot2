from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from constants.tests import FINAL_TEST_ID
from services.test_service import make_single_answer, start_test_flow, send_current_question

from states.test import FinalTestSG

router = Router(name="final_test_router")


# Старт финального теста
@router.callback_query(F.data == "continue:final_test")
async def start_final_test_cb(callback: CallbackQuery, state: FSMContext):
    await start_test_flow(
        callback=callback,
        state=state,
        test_id=FINAL_TEST_ID,
        stage="final_test",
        state_cls=FinalTestSG,
        prefix="ft"
    )


# Ответ с инлайн-кнопки (A/B/C/D)
@router.callback_query(F.data.startswith("ft:ans:"))
async def on_single_answer_final_cb(callback: CallbackQuery, state: FSMContext):
    await make_single_answer(callback, state)
    await send_current_question(callback.message, state, prefix="ft")
