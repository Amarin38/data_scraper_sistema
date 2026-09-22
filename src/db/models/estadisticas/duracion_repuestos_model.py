from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import dbbase


class DuracionRepuestosModel(dbbase):
    __tablename__ = "duracion_repuestos"

    IDDuracionRepuestos: Mapped[int] = mapped_column(primary_key=True)
