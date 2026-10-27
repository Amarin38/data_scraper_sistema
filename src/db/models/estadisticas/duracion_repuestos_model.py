from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import dbbase


class DuracionRepuestosModel(dbbase):
    __tablename__ = "duracion_repuestos"

    IDDuracionRepuestos: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Dominio: Mapped[str] = mapped_column(String(7))
    Cambio: Mapped[int] = mapped_column(SmallInteger)
    FechaInicio: Mapped[date] = mapped_column(Date)
    FechaCambio: Mapped[date] = mapped_column(Date)
    DuracionDias: Mapped[int] = mapped_column(Integer)
    Unidades: Mapped[int] = mapped_column(SmallInteger)
    Censurado: Mapped[bool] = mapped_column(Boolean)
    FechaPatentado: Mapped[date] = mapped_column(Date)

    __table_args__ = (
        Index(
            "idx_duracion_repuesto",
            IDRepuesto,
            postgresql_include=[DuracionDias, FechaPatentado],
            postgresql_where=text('NOT "Censurado"'),
        ),
    )
