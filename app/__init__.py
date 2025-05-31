from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield
    await db.Tortoise.close_connections()


app = FastAPI(lifespan=lifespan, title="KianaFS API")
