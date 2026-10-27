from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import TipoPrevisionEnum
from src.db.session import dbbase


class PrevisionModel(dbbase):
    __tablename__ = "prevision"

    IDPrevision: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Periodo: Mapped[date] = mapped_column(Date)
    Cantidad: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    Metodo: Mapped[TipoPrevisionEnum | None] = mapped_column(
        SAEnum(TipoPrevisionEnum, values_callable=lambda x: [e.value for e in x])
    )
    FechaCalculo: Mapped[date] = mapped_column(Date)
    StockObjetivo: Mapped[int] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint(IDRepuesto, Periodo),)
