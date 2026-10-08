from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import CabecerasEnum
from src.db.session import dbbase


class IndiceConsumoModel(dbbase):
    __tablename__ = "indice_consumo"

    IDIndiceConsumo: Mapped[int] = mapped_column(primary_key=True)
    IDRepuesto: Mapped[int] = mapped_column(ForeignKey("repuesto.IDRepuesto"))
    Deposito: Mapped[CabecerasEnum] = mapped_column(
        SAEnum(CabecerasEnum, values_callable=lambda x: [e.value for e in x])
    )
    Unidades: Mapped[int] = mapped_column(Integer)
    Coches: Mapped[int] = mapped_column(Integer)
    Indice: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    IndiceGlobal: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    IndiceRelativo: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
