from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, SmallInteger, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import CabecerasEnum, TipoMovEnum

from .. import dbbase


class FichaStockModel(dbbase):
    __tablename__ = "ficha_stock"

    IDFichaStock:       Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto:         Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    FechaMov:           Mapped[date] = mapped_column(Date)
    Deposito:           Mapped[CabecerasEnum]   = mapped_column(SAEnum(CabecerasEnum, values_callable=lambda x: [e.value for e in x]))
    TipoMov:            Mapped[TipoMovEnum]     = mapped_column(SAEnum(TipoMovEnum, values_callable=lambda x: [e.value for e in x]))
    Cantidad:           Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    PrecioUnitario:     Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    Usuario:            Mapped[str | None] = mapped_column(String(5))
    DepositoTransfer:   Mapped[int | None] = mapped_column(SmallInteger)
