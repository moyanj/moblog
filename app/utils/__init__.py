from typing import Any, Optional, TypeVar, Generic
import orjson
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class Response(JSONResponse, Generic[T]):

    def __init__(
        self,
        data: Optional[T] = None,
        message: str = "OK",
        status_code: int = 200,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        # 将数据转换为 JSON 兼容的格式
        converted_data = self._convert_data(data)

        # 创建响应字典
        response_dict = {
            "message": message,
            "success": status_code == 200,
            "data": converted_data,
            "status_code": status_code,
        }

        # 初始化父类 JSONResponse
        super().__init__(
            content=response_dict,
            status_code=status_code,
            headers=headers,
        )

    @staticmethod
    def _convert_data(data: Any) -> Any:
        """
        递归地将 Pydantic 模型和嵌套结构转换为字典。
        """
        if isinstance(data, dict):
            return {k: Response._convert_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [Response._convert_data(item) for item in data]
        elif isinstance(data, BaseModel):
            return Response._convert_data(data.model_dump())
        else:
            return data

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "OK") -> "Response[T]":
        """
        创建一个成功的响应，可选的数据和自定义消息。
        """
        return cls(data=data, message=message)

    @classmethod
    def error(cls, message: str = "Error", status_code: int = 500) -> "Response[None]":
        """
        创建一个错误响应，带有自定义消息和状态码。
        """
        return cls(message=message, status_code=status_code)  # type: ignore
