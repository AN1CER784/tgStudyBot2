from typing import List

from database.models.lesson import LessonType

LESSONS: List[dict] = [
    # Вводные материалы
    {
        "name": "Рабочая тетрадь",
        "type": LessonType.free_lesson,
        "description": (
            "Отправляем Вам Рабочую тетрадь. Перед началом обучения рекомендуем её скачать и выполнять в ней все задания.\nСсылка: https://drive.google.com/file/d/1lJB9Fgg9FQk4ElmukNGQMoqAibExieFl/view?usp=sharing"
        ),
    },
    {
        "name": "Вводный урок",
        "type": LessonType.free_lesson,
        "video_message_ids": [2],
        "description": (
            "Мы начинаем наше обучение. Прежде чем продолжить просмотр уроков, пройдите <a href='https://psytests.org/typo/hero.html'>тестирование на архетипы</a> - оно поможет Вам определить Ваши сильные стороны  и тестирование по системе DISC, используя <a href='https://drive.google.com/file/d/1t9VhecwHlYyADDccxQ2SW7OHQbR4QXlX/view?usp=drive_link'>следующий файл</a>"
        ),
    },
    # 1 блок
    {
        "name": '1 блок: "Роль и ответственность старшего администратора". ',
        "type": LessonType.free_lesson,
        "video_message_ids": [3],
        "description": (
            """
Исходя из Ваших результатов тестирования по DISC и Архетипов - пропишите в рабочей тетради Ваш стиль управления, фразы и слова, которые возможно использовать.
            """
        ),
    },
    # 2 блок
    {
        "name": '2 блок: "Управление командой и процессами сервиса. Точки опоры менеджмента в beauty: CJM и менеджмент. Часть 1."',
        "type": LessonType.free_lesson,
        "video_message_ids": [4],
        "description": (
            """
Проведите анализ бизнеса / конкурентный анализ / анализ по стратегической задаче по методу SWOT.
            """
        ),
    },

    {
        "name": '2 блок: "Управление командой и процессами сервиса. Точки опоры менеджмента в beauty: CJM и менеджмент. Часть 2." ',
        "type": LessonType.free_lesson,
        "video_message_ids": [5],
        "description": "Пропишите виды нематериальной мотивации для Ваших сотрудников в команде.",
    },

    {
        "name": '2 блок: "Управление командой и процессами сервиса. Ожидания сотрудников. Часть 3."',
        "type": LessonType.free_lesson,
        "video_message_ids": [6],
        "description":
            """
В рабочей тетради укажите на какой стадии находится каждый сотрудник и что Вам необходимо сделать с учетом 12 вопросов. 
Прочитайте книгу "Сначала нарушьте все правила".
            """
    },

    # 3 блок
    {
        "name": """
3 блок: "Организация процессов сервиса через CJM. Часть 1"
            """,
        "type": LessonType.free_lesson,
        "video_message_ids": [7],
        "description": "",
    },

    {
        "name": '3 блок: "Организация процессов сервиса через CJM. Задание"',
        "type": LessonType.free_lesson,
        "video_message_ids": [8],
        "description": "По каждому этапу CJM пропишите действия команды для усиления сервисной и качественной частей данного этапа и удержания Гостя.",
    },

    {
        "name": '3 блок: "Организация процессов сервиса через CJM. Разбор задания с примерами"',
        "type": LessonType.free_lesson,
        "video_message_ids": [9],
        "description": "",
    },

    {
        "name": '3 блок: "Организация процессов сервиса через CJM. Часть 4"',
        "type": LessonType.task_lesson,
        "video_message_ids": [10],
        "description":
            """
Пропишите 3-5 задач для ваших коллег по SMART и по методу гамбургера. Пришлите в чат одну формулировку задачи / обратной связи по методу гамбургера.
Мы пришлем Вам обратную связь и Вы сможете продолжить мастер-класс. 
            """,
    },

    {
        "name": '3 блок: "Организация процессов сервиса через CJM. Методы анализа и контроля"',
        "type": LessonType.free_lesson,
        "video_message_ids": [11, 12, 13],
        "description": "",
    },

    # 4 блок
    {
        "name": '4 блок: "Управление качеством. Планирование изменений"',
        "type": LessonType.free_lesson,
        "video_message_ids": [14],
        "description": "",
    },
    {
        "name": '4 блок: "Управление качеством. Этапы внедрения сотрудников, коррекция работы и обратная связь. Аттестация"',
        "type": LessonType.free_lesson,
        "video_message_ids": [15],
        "description": "",
    },
    # 5 блок
    {
        "name": '5 блок: "Решение сложных ситуаций',
        "type": LessonType.free_lesson,
        "video_message_ids": [16],
        "description": "",
    },
    # 6 блок
    {
        "name": '6 блок: "Личная эффективность старшего администратора"',
        "type": LessonType.free_lesson,
        "video_message_ids": [17],
        "description": "",
    },
    # 7 блок
    {
        "name": '7 блок: "Финансовая и административная аналитика и отчетность"',
        "type": LessonType.free_lesson,
        "video_message_ids": [18],
        "description":
            """
    Пропишите концептуальные и сезонные метрики для Вашего бизнеса.
    Проверьте свой бизнес по чек-листу метрик в кризис.
            """,
    },
]
