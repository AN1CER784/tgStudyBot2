from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def update_host_message(message: Message, state: FSMContext, text: str, reply_markup=None):
    """
    Редактируем одно и то же 'хост' сообщение.
    Если его ещё нет или нельзя отредактировать — создаём и запоминаем.
    """
    data = await state.get_data()
    host_mid = data.get("host_mid")
    chat_id = message.chat.id

    if host_mid:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=host_mid,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            return
        except TelegramBadRequest as e:
            s = str(e).lower()
            # если текст не изменился — просто обновим клавиатуру
            if "message is not modified" in s:
                try:
                    await message.bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=host_mid,
                        reply_markup=reply_markup
                    )
                    return
                except TelegramBadRequest:
                    pass
            # если сообщение удалено/недоступно — упадём ниже и создадим новое

    # создаём новое “хост-сообщение” и запоминаем id
    sent = await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=True)
    await state.update_data(host_mid=sent.message_id)

