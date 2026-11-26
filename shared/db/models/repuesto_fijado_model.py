from datetime import date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.session import dbbase


class RepuestoFijadoModel(dbbase):
    __tablename__ = "repuesto_fijado"

    IDUsuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.IDUsuario", ondelete="CASCADE"), primary_key=True
    )
    IDRepuesto: Mapped[int] = mapped_column(
        ForeignKey("repuesto.IDRepuesto", ondelete="CASCADE"), primary_key=True
    )
    FechaAlta: Mapped[date] = mapped_column(server_default=func.current_date())
