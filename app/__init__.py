from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from . import db
from .config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    logger.info(f"Running at {config.host}:{config.port}")
    await db.init_db()
    logger.info("Started successfully")
    yield
    await db.Tortoise.close_connections()


app = FastAPI(lifespan=lifespan, title="MoBlog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cros_origin.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> str:
    return "Welcome to MoBlog backend!"
