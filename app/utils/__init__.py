from fastapi import Response as FastapiResponse
import orjson
from pydantic import BaseModel
from typing import Any, Optional


class Response(FastapiResponse):

    def __init__(
        self,
        data: Any = None,
        msg: str = "OK",
        code: int = 200,
        headers: Optional[dict[str, str]] = None,
    ):
        d = {
            "msg": msg,
            "success": code == 200,
            "data": self._convtype(data),
            "status_code": code,
        }
        super().__init__(
            content=orjson.dumps(d),
            media_type="application/json",
            status_code=code,
            headers=headers,
        )

    def _convtype(self, data):
        if isinstance(data, dict):
            return {self._convtype(k): self._convtype(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convtype(v) for v in data]
        elif isinstance(data, BaseModel):
            return self._convtype(data.model_dump())
        else:
            return data
