import bcrypt

from fastapi import APIRouter, Depends

import app.utils.auth as auth
from app.schema import User
from app.utils import Response

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
    out = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar": user.avatar,
        "updated_at": user.updated_at.isoformat(timespec="seconds"),
        "created_at": user.created_at.isoformat(timespec="seconds"),
    }
    return Response(out)
