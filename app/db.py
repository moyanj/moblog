from tortoise import Tortoise

from .config import server_config
from .schema import *

ORM_CONFIG = {
    "connections": {
        "default": server_config.db_url,
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "app.schema"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}


async def init_db():
    await Tortoise.init(ORM_CONFIG)

    await Tortoise.generate_schemas(safe=True)
    await Config.init()
