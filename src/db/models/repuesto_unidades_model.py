from datetime import date

from sqlalchemy import Date, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import dbbase


class RepuestoUnidadesModel(dbbase):
    __tablename__ = "repuesto_unidades"
    __table_args__ = (UniqueConstraint("IDRepuesto", "FechaDesde"),)

    IDRepuestoUnidades: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Unidades: Mapped[int] = mapped_column(SmallInteger)
    FechaDesde: Mapped[date] = mapped_column(Date)
    FechaHasta: Mapped[date | None] = mapped_column(Date)
