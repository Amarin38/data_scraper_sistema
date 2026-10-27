from pydantic import BaseModel


class LoginIn(BaseModel):
    user: str
    password: str
