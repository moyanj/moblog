from tortoise import Tortoise
from .config import config


async def init_db():
    await Tortoise.init(
        db_url=config.db_url,
        modules={"models": ["app.schema"]},
        use_tz=True,
        timezone="UTC+8",
    )

    await Tortoise.generate_schemas()
