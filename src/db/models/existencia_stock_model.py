from src.core.enums import UnidadEnum
from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import Enum as SAEnum
from .. import dbbase


class ExistenciaStockModel(dbbase):
    __tablename__ = "existencia_stock"

    IDExistencia:       Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto:         Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Nombre:             Mapped[str] = mapped_column(String(150))
    Unidad:             Mapped[UnidadEnum | None] = mapped_column(SAEnum(UnidadEnum, values_callable=lambda x: [e.value for e in x]))
    Stock:              Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    FechaExistencia:    Mapped[date] = mapped_column(Date)
    Cabecera:           Mapped[str] = mapped_column(String(30))
