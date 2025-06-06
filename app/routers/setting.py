from typing import Mapping

from fastapi import APIRouter, Depends

from app.schema import Config
from app.utils import Response
from app.utils.auth import get_current_user

router = APIRouter(prefix="/setting")


@router.get("/get_all")
async def get_all() -> Response[Mapping[str, str]]:
    raw = await Config.all()
    return Response.success({item.key: item.value for item in raw})


@router.post("/set")
async def set_val(key: str, value: str, user=Depends(get_current_user)):
    """
    设置配置项
    """
    await Config.set_val(key, value)
    return Response.success()


@router.get("/init")
async def init(user=Depends(get_current_user)):
    """
    重新初始化配置
    """
    if not user.is_admin:
        return Response.error("No permission", 403)
    await Config.set_val("init", "n")
    await Config.init()
    return Response.success()


@router.get("/is_init")
async def get_init():
    """
    获取初始化状态
    """
    return Response.success(await Config.get_val("init", "n") == "y")
