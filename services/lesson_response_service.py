from dataclasses import dataclass
from typing import Optional, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from renderers.lesson import lesson_response_renderer
from services.notify_service import notify_curators_about_response

Event = Union[Message, CallbackQuery]


@dataclass
class Ctx:
    user: "user"
    lesson: "lesson"
    lesson_id: int


async def _reply(event: Event, text: str, **kwargs):
    if isinstance(event, Message):
        return await event.answer(text, **kwargs)
    else:
        return await event.message.answer(text, **kwargs)


async def _get_state_lesson_id(state: FSMContext) -> Optional[int]:
    data = await state.get_data()
    return data.get("current_lesson_id")


async def load_ctx(event: Event, state: FSMContext, expected_type: Optional[str] = None) -> Optional[Ctx]:
    """
    Единая проверка: есть ли активный урок, совпадает ли тип ответа, загрузка user/lesson.
    Возвращает Ctx или None (если уже ответили пользователю и state очищен).
    """
    lesson_id = await _get_state_lesson_id(state)
    if not lesson_id:
        await _reply(event, "Не найдено активное задание. Введите /continue.")
        await state.clear()
        return None

    from database.models import Lesson  # чтобы не плодить импорты наверху
    lesson = await Lesson.get(id=lesson_id)
    if expected_type and lesson.response_type != expected_type:
        await _reply(
            event,
            "Это задание требует "
            + ("текстовый ответ." if lesson.response_type == "text" else "ответ в виде файла.")
        )
        return None

    from database.crud.user import get_user
    if isinstance(event, Message):
        uid = event.from_user.id
    else:
        uid = event.from_user.id
    user = await get_user(user_id=uid)
    return Ctx(user=user, lesson=lesson, lesson_id=lesson_id)


async def finalize_submission(event: Event, state: FSMContext, ctx: Ctx, response_id: int, response_text: str):
    """
    Единая логика «подтвердить пользователю + уведомить кураторов + обновить прогресс + очистить state».
    """
    await _reply(
        event,
        "✅ Ваш ответ отправлен. Сейчас задание на проверке у куратора.\n"
        "Следующий урок откроется после проверки текущего."
    )

    notify_text = lesson_response_renderer(user=ctx.user, lesson=ctx.lesson, response_text=response_text)
    await notify_curators_about_response(response_id=response_id, response_text=notify_text)

    ctx.user.progress.current_stage = "lesson_on_completion"
    await ctx.user.progress.save()

    await state.clear()
