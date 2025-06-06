from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from . import db
from .config import server_config
from .routers import auth_router, setting_router
from .utils import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    logger.info(f"Running at {server_config.host}:{server_config.port}")
    await db.init_db()
    logger.info("Started successfully")

    app.include_router(setting_router)
    app.include_router(auth_router)

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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return Response(message=exc.detail, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return Response(data=exc.errors(), message="Request is Invalid", status_code=400)


@app.get("/")
async def root() -> str:
    return "Welcome to MoBlog backend!"
