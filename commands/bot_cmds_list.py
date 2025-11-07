from aiogram.types import BotCommand


all_cmds = [
    BotCommand(command='start', description='Начать работу с ботом'),
    BotCommand(command='continue', description='Перейти к текущему доступному этапу'),
    BotCommand(command='profile', description='Просмотреть информацию о себе'),
    BotCommand(command='edit', description='Отредактировать информацию о себе'),
]
curator_cmds = [
    BotCommand(command='curator', description='Панель куратора'),
] + all_cmds

admin_cmds = [
    BotCommand(command='admin', description='Панель администратора'),
] + curator_cmds  + all_cmds


