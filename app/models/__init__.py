from token import OP
from pydantic import BaseModel, Field
from typing import Optional


class UserUpdateModel(BaseModel):
    username: Optional[str] = Field(None, description="UserName")
    avatar: Optional[str] = Field(None, description="Avatar")
    is_admin: Optional[bool] = Field(None, description="Is admin")
    password: Optional[str] = Field(None, description="Password")


class UserRegisterModel(BaseModel):
    username: str = Field(..., description="UserName")
    password: str = Field(..., description="Password")


class PostCreateModel(BaseModel):
    title: str = Field(..., description="Title")
    summary: str = Field(..., description="Summary")
    content: str = Field(..., description="Content")
    category_id: int = Field(..., description="Category ID")
    tag_names: list[str] = Field(..., description="Tag IDs")


class PostUpdateModel(BaseModel):
    title: Optional[str] = Field(..., description="Title")
    summary: Optional[str] = Field(..., description="Summary")
    content: Optional[str] = Field(..., description="Content")
    category_id: Optional[int] = Field(..., description="Category ID")
    tag_names: Optional[list[str]] = Field(..., description="Tag IDs")
