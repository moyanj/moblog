from typing import Mapping
import bcrypt

from fastapi import APIRouter, Depends

import app.utils.auth as auth
from app.schema import User
from app.utils import Response
from app.models import UserUpdateModel

router = APIRouter(prefix="/auth")


@router.get("/verify")
async def verify_token(token: str):
    return Response(auth.verify_token(token))


@router.post("/register")
async def register(name: str, email: str, password: str):
    if (await User.get_or_none(email=email)) is not None:
        return Response(None, "Email already exists", 400)

    if auth.check_pwd_policy(password) is False:
        return Response(None, "Password is too weak", 400)

    # 生成 16 字节的盐
    salt = bcrypt.gensalt(rounds=12)  # 使用 bcrypt 生成盐

    # 使用 bcrypt 对密码进行哈希
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    u = User(
        name=name, email=email, password=hashed_password.decode(), salt=salt.decode()
    )
    await u.save()

    return Response(auth.make_token(u))


@router.post("/token")
async def login(email: str, password: str):
    u = await User.get_or_none(email=email)
    if u is None:
        return Response(None, "User not found", 404)

    # 使用 bcrypt 验证密码
    if not bcrypt.checkpw(password.encode(), u.password.encode()):
        return Response(None, "Password is incorrect", 401)

    return Response(auth.make_token(u))


@router.get("/me")
async def me(user: User = Depends(auth.get_current_user)):
    return Response(user.to_safe_dict())


@router.get("/remove/{id}")
async def remove(id: int, user: User = Depends(auth.get_current_user)):
    if not user.is_admin:
        return Response.error("No permission", 403)

    target = await User.get_or_none(id=id)
    if target is None:
        return Response.error("User not found", 404)

    await target.delete()
    return Response.success()


@router.post("/update/{id}")
async def update(
    id: int, data: UserUpdateModel, user: User = Depends(auth.get_current_user)
):
    # 检查是否需要管理员权限
    need_admin = False
    if data.is_admin is not None:
        need_admin = True
    if id != user.id:
        need_admin = True
    if need_admin:
        if not user.is_admin:
            return Response.error("No permission", 403)

    # 获取目标用户
    target = await User.get_or_none(id=id)
    if target is None:
        return Response.error("User not found", 404)

    # 准备更新数据
    data_dict = data.model_dump(exclude_unset=True)
    # 处理密码更新
    if data.password:
        # 生成 16 字节的盐
        salt = bcrypt.gensalt(rounds=12)  # 使用 bcrypt 生成盐
        # 使用 bcrypt 对密码进行哈希
        hashed_password = bcrypt.hashpw(data.password.encode(), salt).decode()
        data_dict["password"] = hashed_password
        data_dict["salt"] = salt.decode()

    # 更新目标用户信息
    await target.update_from_dict(data_dict).save()
    return Response.success(target.to_safe_dict())
