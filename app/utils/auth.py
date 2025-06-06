from datetime import datetime, timedelta
import re

import jwt
from fastapi import HTTPException

from app.config import server_config
from app.schema import User


def make_token(user: User, exp=24):
    print(server_config.secret_key)
    now = datetime.now()
    exp = now + timedelta(hours=exp)
    playload = {
        "exp": int(exp.timestamp()),
        "data": user.id,
    }
    return jwt.encode(playload, server_config.secret_key, algorithm="HS256")


def verify_token(token: str):
    print(server_config.secret_key)
    try:
        playload = jwt.decode(token, server_config.secret_key, algorithms=["HS256"])
        return playload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(e)
        return None


def check_pwd_policy(password: str):
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


async def get_current_user(token: str):
    print(token)
    playload = verify_token(token)
    if not (playload is None):
        user = await User.get_or_none(id=int(playload["data"]))
        if user is not None:
            return user
        else:
            print("User not found")
            raise HTTPException(status_code=401, detail="Invalid token")
    raise HTTPException(status_code=401, detail="Invalid token")
