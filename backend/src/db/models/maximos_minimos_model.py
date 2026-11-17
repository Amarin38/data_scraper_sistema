from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import CabecerasEnum

from .. import dbbase


class MaximosMinimosModel(dbbase):
    __tablename__ = "maximos_minimos"

    IDMaximosMinimos: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Deposito: Mapped[CabecerasEnum] = mapped_column(
        SAEnum(CabecerasEnum, values_callable=lambda x: [e.value for e in x])
    )
    DemandaMensual: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    MesesConDatos: Mapped[int] = mapped_column(Integer)
    FechaCalculo: Mapped[date] = mapped_column(Date)
