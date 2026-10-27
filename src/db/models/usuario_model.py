from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    String,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import TipoUsuarioLoginEnum

from .. import dbbase


class UsuarioModel(dbbase):
    __tablename__ = "usuario"

    IDUsuario: Mapped[int] = mapped_column(primary_key=True)
    User: Mapped[str] = mapped_column(String(50), unique=True)
    PasswordHash: Mapped[str] = mapped_column(String(255))
    TipoUser: Mapped[TipoUsuarioLoginEnum] = mapped_column(
        SAEnum(TipoUsuarioLoginEnum, values_callable=lambda x: [e.value for e in x]),
        default=TipoUsuarioLoginEnum.USER,
    )
    Activo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    UltimoLogin: Mapped[date | None] = mapped_column(Date)
