from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class ExistenciaStockModel(dbbase):
    __tablename__ = "existencia_stock"

    IDExistencia: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Stock: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    FechaExistencia: Mapped[date] = mapped_column(Date)
    Cabecera: Mapped[str] = mapped_column(String(30))

    __table_args__ = (
        UniqueConstraint("IDRepuesto"),
        Index("idx_existencia_repuesto", IDRepuesto),
    )
