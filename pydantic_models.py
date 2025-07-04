from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator


class UserModel(BaseModel):
    username: str
    password: str
    email: EmailStr
    name: Optional[str] = None
    bio: Optional[str] = None


class UserModelResponse(BaseModel):
    id: str
    username: str
    email: str
    name: Optional[str] = None
    bio: Optional[str] = None


class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"