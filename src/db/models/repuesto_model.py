from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import TipoDuracionEnum

from .. import dbbase


class RepuestoModel(dbbase):
    __tablename__ = "repuesto"
    __table_args__ = (UniqueConstraint("Familia", "Articulo"),)

    IDRepuesto: Mapped[int] = mapped_column(primary_key=True)
    Familia: Mapped[str] = mapped_column(String(3))
    Articulo: Mapped[str] = mapped_column(String(5))
    Descripcion: Mapped[str] = mapped_column(String(100))
    Conjunto: Mapped[str | None] = mapped_column(String(50))
    Condicion: Mapped[str] = mapped_column(String(8))
    TipoDuracion: Mapped[TipoDuracionEnum | None] = mapped_column(
        SAEnum(TipoDuracionEnum, values_callable=lambda x: [e.value for e in x])
    )
    Critico: Mapped[bool] = mapped_column(Boolean)
