from pydantic import BaseModel


class LoginIn(BaseModel):
    user: str
    password: str


class PreferenciasIn(BaseModel):
    modo_noche: bool
