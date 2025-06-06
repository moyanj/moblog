from typing import Optional
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    username: str = Field(description="UserName")
    avatar: str = Field(description="Avatar")
    is_admin: bool = Field(description="Is admin")
    created_at: str = Field(..., description="Created at")
    updated_at: str = Field(..., description="Updated at")


class PostInfo(BaseModel):
    id: int = Field(..., description="ID")
    title: str = Field(..., description="Title")
    summary: str = Field(..., description="Summary")
    content: str = Field(..., description="Content")
    category: str = Field(..., description="Category")
    tags: list[str] = Field(..., description="Tags")
    author: str = Field(..., description="Author")
    created_at: str = Field(..., description="Created at")
    updated_at: str = Field(..., description="Updated at")
