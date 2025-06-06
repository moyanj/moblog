from typing import Optional
import bcrypt

from fastapi import APIRouter, Depends, HTTPException

import app.utils.auth as auth
from app.schema import User
from app.utils import Response
from app.models import UserUpdateModel

router = APIRouter()

UserID = int | str


def convert_user_id(id: UserID, user):
    if id == "me":
        if user is None:
            raise HTTPException(status_code=400, detail="Not logged in yet")
        return user.id
    else:
        return id


@router.post("/login")
async def login(name: str, password: str):
    u = await User.get_or_none(name=name)
    if u is None:
        return Response(None, "User not found", 404)

    # 使用 bcrypt 验证密码
    if not bcrypt.checkpw(password.encode(), u.password.encode()):
        return Response(None, "Password is incorrect", 401)

    return Response(auth.make_token(u))


@router.post("/user")
async def register(name: str, password: str):
    if (await User.get_or_none(name=name)) is not None:
        return Response(None, "Email already exists", 400)

    if auth.check_pwd_policy(password) is False:
        return Response(None, "Password is too weak", 400)

    # 生成 16 字节的盐
    salt = bcrypt.gensalt(rounds=12)  # 使用 bcrypt 生成盐

    # 使用 bcrypt 对密码进行哈希
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    u = User(name=name, password=hashed_password.decode(), salt=salt.decode())
    await u.save()

    return Response(auth.make_token(u))


@router.get("/user/{id}")
async def get_user(id: UserID, user: Optional[User] = Depends(auth.get_current_user)):
    id = convert_user_id(id, user)
    u = await User.get_or_none(id=id)
    if u is None:
        return Response(None, "User not found", 404)
    return Response(u.to_safe_dict())


@router.delete("/user/{id}")
async def remove_user(id: UserID, user: User = Depends(auth.get_current_user)):
    id = convert_user_id(id, user)
    if not user.is_admin:
        return Response.error("No permission", 403)

    target = await User.get_or_none(id=id)
    if target is None:
        return Response.error("User not found", 404)

    await target.delete()
    return Response.success()


@router.put("/user/{id}")
async def update_user(
    id: UserID, data: UserUpdateModel, user: User = Depends(auth.get_current_user)
):
    id = convert_user_id(id, user)
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
