from typing import List, Iterable

from constants.tests import ABC
from database.models import Question, Option, QType, Test, Attempt, Answer


def render_question_block(q: Question, options: List[Option], index: int, total: int) -> str:
    head = f"<b>Вопрос {index}/{total}</b>\n\n{q.text}"
    if q.type == QType.single and options:
        lines = []
        for letter, opt in zip(ABC, sorted(options, key=lambda o: o.order)[:4]):
            lines.append(f"{letter}) {opt.text}")
        return head + "\n\n" + "\n".join(lines)
    return head + "\n\nНапиши ответ сообщением."


def render_test_results(test: Test, passed: bool, percent: float):
    status = "✅ <b>Поздравляем! Ваш Результат составил:</b>" if passed else "❌ <b>Ваш Результат составил:</b>"
    text = f"{status}\n <b>{percent}%</b>\n"

    fail_message = test.fail_message
    normal_success_message = test.normal_success_message
    perfect_completion_message = test.perfect_success_message
    if not passed and fail_message:
        return text + fail_message
    elif percent >= 50 and normal_success_message:
        return text + normal_success_message
    elif percent >= 85 and perfect_completion_message:
        return text + perfect_completion_message
    return text


def render_user_attempt(answer: Attempt, answers: Iterable[Answer]):
    test = answer.test
    questions = test.questions
    text = f"<b>Результаты теста</b>\n\n<b>Тест:</b> {test.title}\n\n"
    text += f"Пользователь: {answer.user.full_name}\n"
    text += f"Дата прохождения: {answer.finished_at:%d.%m.%Y}\n"
    text += f"Процент правильных ответов: {answer.score / answer.max_score * 100:.2f}%"
    for question, answer in zip(questions, answers):
        if question.type == QType.single:
            options = question.options

            text += f"\n\n<b>Вопрос {question.order}:</b> {question.text}\n"
            if answer.is_correct:
                text += f"\nОтвет пользователя зачтен ✅\n"
            else:
                text += f"\nОтвет пользователя не зачтен❌\n"

            text += f"Ответ пользователя: {answer.selected_option.text}\n"

            text += "\nВарианты ответа:\n"
            for option in options:
                if option.is_correct:
                    text += f"✅ {option.text}\n"
                else:
                    text += f"❌ {option.text}\n"
        elif question.type == QType.text:
            text += f"Ответ пользователя: {answer.text_answer}\n\n"
    return text