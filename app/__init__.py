from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from . import db
from .config import server_config
from .routers import auth_router, setting_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    logger.info(f"Running at {server_config.host}:{server_config.port}")
    await db.init_db()
    logger.info("Started successfully")
    yield
    await db.Tortoise.close_connections()


app = FastAPI(lifespan=lifespan, title="MoBlog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.cros_origin.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(setting_router)
app.include_router(auth_router)


@app.get("/")
async def root() -> str:
    return "Welcome to MoBlog backend!"
