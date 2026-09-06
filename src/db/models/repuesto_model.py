from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class RepuestoModel(dbbase):
    __tablename__ = "repuesto"

    IDRepuesto:         Mapped[int] = mapped_column(primary_key=True)
    Familia:            Mapped[str] = mapped_column(String(3))
    Articulo:           Mapped[str] = mapped_column(String(5))
    Descripcion:        Mapped[str] = mapped_column(String(100))

    __table_args__ = (UniqueConstraint("Familia", "Articulo"),)
