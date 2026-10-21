from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, BigInteger, Date, ForeignKey, Index, SmallInteger
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import CabecerasEnum, TipoMovEnum, TipoUsuarioEnum

from .. import dbbase


class FichaStockModel(dbbase):
    __tablename__ = "ficha_stock"

    IDFichaStock: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    FechaMov: Mapped[date] = mapped_column(Date)
    Deposito: Mapped[CabecerasEnum] = mapped_column(
        SAEnum(CabecerasEnum, values_callable=lambda x: [e.value for e in x])
    )
    TipoMov: Mapped[TipoMovEnum] = mapped_column(
        SAEnum(TipoMovEnum, values_callable=lambda x: [e.value for e in x])
    )
    Cantidad: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    PrecioUnitario: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    Interno: Mapped[int | None] = mapped_column(SmallInteger)
    TipoUsuario: Mapped[str | None] = mapped_column(
        SAEnum(TipoUsuarioEnum, values_callable=lambda x: [e.value for e in x])
    )
    DepositoTransfer: Mapped[int | None] = mapped_column(SmallInteger)

    __table_args__ = (
        Index(
            "idx_ficha_fecha_id",
            FechaMov.desc(),
            IDFichaStock,
        ),
    )
