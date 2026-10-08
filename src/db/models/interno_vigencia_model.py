from datetime import date

from sqlalchemy import Date, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import dbbase


class InternoVigenciaModel(dbbase):
    __tablename__ = "interno_vigencia"

    __table_args__ = (
        UniqueConstraint("Dominio", "FechaDesde"),
        Index("ix_interno_vigencia_lookup", "Interno", "FechaDesde", "FechaHasta"),
    )

    IDInternoVigencia: Mapped[int] = mapped_column(primary_key=True)
    Dominio: Mapped[str] = mapped_column(String(7))
    Interno: Mapped[int] = mapped_column(SmallInteger)
    FechaDesde: Mapped[date] = mapped_column(Date)
    FechaHasta: Mapped[date | None] = mapped_column(Date)
    FechaPatentado: Mapped[date | None] = mapped_column(Date)
