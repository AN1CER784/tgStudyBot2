from tortoise import Tortoise

from config import DATABASE_URL

CONFIG = {
    "connections": {
        "default": DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        }
    }
}


async def init_db():
    await Tortoise.init(config=CONFIG)


async def close_db():
    await Tortoise.close_connections()
