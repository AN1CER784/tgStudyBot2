from telethon import TelegramClient

from config import GROUP_CHAT_ID, API_ID, API_HASH

# Инициализация Telethon клиента
api_id = int(API_ID)
api_hash = API_HASH
client = TelegramClient('session_name', api_id, api_hash)


def get_video_ids_from_group():
    video_ids = []  # Список для хранения ID видео-сообщений

    print("Подключаемся к Telegram...")

    # Подключаемся к Telegram сессии
    client.start()  # Нет необходимости в client.connect()

    print("Подключение прошло успешно!")

    # Получаем историю сообщений из группы
    print("Получаем сообщения из группы...")

    for msg in client.iter_messages(int(GROUP_CHAT_ID), limit=100):  # Можно увеличить лимит, если нужно
        if msg.video:  # Проверяем, что сообщение содержит видео
            print(f"Найдено видео! ID: {msg.id}")
            video_ids.append(msg.id)  # Добавляем ID сообщения с видео

    client.disconnect()  # Закрываем соединение

    print(f"Собрано {len(video_ids)} ID видео.")

    return video_ids


# Запуск клиента


video_ids = get_video_ids_from_group()
print("Собранные ID видео:", video_ids)
