import re
from datetime import datetime, timedelta
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from app.config import server_config
from app.schema import User


def make_token(user: User, exp=24):
    print(server_config.secret_key)
    now = datetime.now()
    exp = now + timedelta(hours=exp)
    playload = {
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "data": user.username,
    }
    return jwt.encode(playload, server_config.secret_key, algorithm="HS256")


def verify_token(token: str):
    try:
        playload = jwt.decode(token, server_config.secret_key, algorithms=["HS256"])
        return playload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        return None


def check_pwd_policy(password: str):
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


security_scheme = HTTPBearer(auto_error=False)


async def extract_token(
    request: Request,
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(security_scheme)
    ],
) -> Optional[str]:
    # 优先级 1: Authorization header
    if credentials:
        return credentials.credentials

    # 优先级 2: Cookie
    if token := request.cookies.get("token"):
        return token

    # 优先级 3: JSON body (安全获取方式)
    try:
        if body := await request.json():
            return body.get("token")  # type: ignore
    except Exception:
        pass

    return None


async def get_current_user(token: Annotated[str, Depends(extract_token)]) -> User:
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = verify_token(token)
        username = payload["data"]  # type: ignore
    except (ValidationError, ValueError, KeyError) as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    if not (user := await User.get_or_none(username=username)):
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
