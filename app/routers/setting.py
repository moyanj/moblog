from typing import Mapping
from fastapi import APIRouter

from app.schema import Config
from app.utils import Response

router = APIRouter(prefix="/setting")


@router.get("/get_all")
async def get_all() -> Response[Mapping[str, str]]:
    raw = await Config.all()
    return Response.success({item.key: item.value for item in raw})


@router.post("/set")
async def set_val(key: str, value: str):
    """
    设置配置项
    """
    await Config.set_val(key, value)
    return Response.success()


@router.get("/init")
async def init():
    """
    重新初始化配置
    """
    await Config.set_val("init", "n")
    await Config.init()
    return Response.success()


@router.get("/is_init")
async def get_init():
    """
    获取初始化状态
    """
    return Response.success(await Config.get_val("init", "n") == "y")
