from typing import Literal

from commands.bot_cmds_list import all_cmds, curator_cmds, admin_cmds
from config import bot


async def set_commands(role: Literal['admin', 'user', 'curator']):
    if role == 'admin':
        await bot.set_my_commands(admin_cmds)
    elif role == 'curator':
        await bot.set_my_commands(curator_cmds)
    else:
        await bot.set_my_commands(all_cmds)
