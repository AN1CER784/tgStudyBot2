import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from constants.tests import ENTRY_TEST_ID
from services.test_service import send_current_question, start_test_flow, make_single_answer, make_text_answer_and_next
from states.test import EntryTestSG

router = Router(name='entry_test_router')
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "continue:entry_test")
async def start_entry_test_cb(callback: CallbackQuery, state: FSMContext):
    await start_test_flow(
        callback=callback,
        state=state,
        test_id=ENTRY_TEST_ID,
        stage="entry_test",
        state_cls=EntryTestSG,
        prefix="et",
    )


@router.callback_query(F.data.startswith("et:ans:"))
async def on_single_answer_cb(callback: CallbackQuery, state: FSMContext):
    await make_single_answer(callback, state)
    await send_current_question(callback.message, state, prefix="et")


# ---------- ОТВЕТЫ TEXT (НЕ учитываем в статистике) ----------

@router.message(EntryTestSG.answering)
async def on_text_answer_message(message: Message, state: FSMContext):
    await make_text_answer_and_next(message, state)
