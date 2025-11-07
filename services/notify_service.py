from database.crud.user import get_curators, get_admins
from keyboards.curator_keyboards import curator_detail_kb, curator_final_comment_kb
from utils.send_message_safely import send_message_safely


async def notify_curators_about_response(response_text: str, response_id: int):
    """
    Уведомляет кураторов у выполненном задании
    """
    await notify_curators_about_submission(response_text, curator_detail_kb(response_id=response_id))


async def notify_curators_about_test_completion(submission_text: str, attempt_id: int):
    """
    Уведомляет кураторов у выполненном тесте
    """
    await notify_curators_about_submission(submission_text, reply_markup=curator_final_comment_kb(attempt_id))


async def notify_curators_about_submission(submission_text: str, reply_markup=None):
    """
    Уведомляет кураторов у выполненном задании
    """
    curators = await get_curators()
    admins = await get_admins()

    for curator in curators:
        await send_message_safely(curator.id, submission_text, reply_markup=reply_markup)

    for admin in admins:
        await send_message_safely(admin.id, submission_text, reply_markup=reply_markup)


async def notify_user_about_submission(user_id: int, message_text: str):
    """
    Уведомляет пользователя о выполнении задания
    """
    await send_message_safely(user_id, message_text)
