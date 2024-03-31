from pydantic import BaseModel


class User:
    username: str
    password: str


class Token:
    access_token: str
    token_type: str
