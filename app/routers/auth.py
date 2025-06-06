from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException

import app.utils.auth as auth
from app.models import UserRegisterModel, UserUpdateModel
from app.schema import User
from app.utils import Response

router = APIRouter()

UserID = str


def convert_user_id(id: UserID, user):
    if id == "me":
        if user is None:
            raise HTTPException(status_code=400, detail="Not logged in yet")
        return user.username
    else:
        return id


@router.post("/login")
async def login(username: str, password: str) -> Response[str]:
    u = await User.get_or_none(username=username)
    if u is None:
        return Response.error("User not found", 404)

    # 使用 bcrypt 验证密码
    if not bcrypt.checkpw(password.encode(), u.password.encode()):
        return Response.error("Password is incorrect", 401)

    return Response.success(auth.make_token(u))


@router.get("/user")
async def get_users(user: User = Depends(auth.get_current_user)):
    return Response.success([user.to_safe_dict() for user in await User.all()])


@router.post("/user")
async def register(data: UserRegisterModel):
    if data.username == "me":
        return Response.error("Username is not allowed", 400)
    if (await User.get_or_none(username=data.username)) is not None:
        return Response.error("Username already exists", 400)

    if auth.check_pwd_policy(data.password) is False:
        return Response.error("Password is too weak", 400)

    # 生成 16 字节的盐
    salt = bcrypt.gensalt(rounds=12)  # 使用 bcrypt 生成盐

    # 使用 bcrypt 对密码进行哈希
    hashed_password = bcrypt.hashpw(data.password.encode(), salt)

    u = User(username=data.username, password=hashed_password.decode())

    if not User.exists():
        u.update_from_dict(
            {
                "is_admin": True,
            }
        )

    await u.save()

    return Response.success(auth.make_token(u))


@router.get("/user/{username}")
async def get_user(
    username: str, user: Optional[User] = Depends(auth.get_current_user)
):
    username = convert_user_id(username, user)
    u = await User.get_or_none(username=username)
    if u is None:
        return Response.error("User not found", 404)
    return Response.success(u.to_safe_dict())


@router.delete("/user/{username}")
async def remove_user(username: str, user: User = Depends(auth.get_current_user)):
    username = convert_user_id(username, user)
    if not user.is_admin:
        return Response.error("No permission", 403)

    target = await User.get_or_none(username=username)
    if target is None:
        return Response.error("User not found", 404)

    await target.delete()
    return Response.success()


@router.put("/user/{username}")
async def update_user(
    username: str, data: UserUpdateModel, user: User = Depends(auth.get_current_user)
):
    username = convert_user_id(username, user)
    # 检查是否需要管理员权限
    need_admin = False
    if data.is_admin is not None:
        need_admin = True
    if username != user.username:
        need_admin = True
    if need_admin:
        if not user.is_admin:
            return Response.error("No permission", 403)

    # 获取目标用户
    target = await User.get_or_none(username=username)
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

    # 更新目标用户信息
    await target.update_from_dict(data_dict).save()
    return Response.success(target.to_safe_dict())
