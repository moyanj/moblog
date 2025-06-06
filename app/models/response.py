from typing import Optional

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    username: str = Field(description="UserName")
    avatar: Optional[str] = Field(description="Avatar")
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


class GetPostResult(BaseModel):
    total: int = Field(..., description="Count")
    posts: list[PostInfo] = Field(..., description="Posts")
    page: int = Field(..., description="Page")
    per_page: int = Field(..., description="Per page")


class TagInfo(BaseModel):
    id: int
    name: str


class CategoryInfo(BaseModel):
    id: int
    name: str
