from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.session import dbbase


class UsuarioPreferencia(dbbase):
    __tablename__ = "usuario_preferencia"

    IDUsuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.IDUsuario", ondelete="CASCADE"), primary_key=True
    )
    Clave: Mapped[str] = mapped_column(primary_key=True)
    Valor: Mapped[dict[str, Any]] = mapped_column(JSONB)
    Actualizado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
