from pydantic import BaseModel
from enum import Enum


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    fullname: str
    username: str
    password: str
    email: str
    role: UserRole


class LoginUser(BaseModel):
    username: str
    password: str
