from pydantic import BaseModel, Field
from typing import Optional


class UserUpdateModel(BaseModel):
    email: Optional[str] = Field(None, description="Email")
    name: Optional[str] = Field(None, description="Name")
    avatar: Optional[str] = Field(None, description="Avatar")
    is_admin: Optional[bool] = Field(None, description="Is admin")
    password: Optional[str] = Field(None, description="Password")
