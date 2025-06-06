from tortoise import Tortoise

from .config import server_config
from .schema import *


async def init_db():
    await Tortoise.init(
        db_url=server_config.db_url,
        modules={"models": ["app.schema"]},
        use_tz=True,
    )

    await Tortoise.generate_schemas()
    await Config.init()
