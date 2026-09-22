from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import dbbase


class ConteoStockModel(dbbase):
    __tablename__ = "estadistica_conteo_stock"

    IDConteoStock: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    FechaConteo: Mapped[date] = mapped_column(Date)
    Sistema: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    Recuento: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    DiferenciaStock: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    Estanteria: Mapped[str | None] = mapped_column(String(50))
    PrecioActual: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    PrecioAnterior: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
