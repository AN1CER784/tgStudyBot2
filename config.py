from json import loads
from os import getenv

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

ADMINS = loads(getenv('ADMINS'))  # список админов
BOT_ADDRESS = getenv('BOT_ADDRESS')  # адрес бота в ТГ
TOKEN = getenv('TOKEN')  # токен бота телеграм
GROUP_CHAT_ID = getenv('GROUP_CHAT_ID')  # id группы в ТГ для видео
API_ID = getenv('API_ID')
API_HASH = getenv('API_HASH')
REVIEW_CHAT_ID = getenv('REVIEW_CHAT_ID')

DB_USER = getenv('POSTGRES_USER')  # имя пользователя БД
DB_PASSWORD = getenv('POSTGRES_PASSWORD')  # пароль пользователя БД
DB_NAME = getenv('POSTGRES_DB')  # название БД
DB_HOST = getenv('POSTGRES_HOST')  # хост БД
DB_PORT = getenv('POSTGRES_PORT')  # порт БД

# ссылка для доступа к БД
DATABASE_URL = f'postgres://{DB_USER}:{DB_PASSWORD}@db:5432/{DB_NAME}'

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))