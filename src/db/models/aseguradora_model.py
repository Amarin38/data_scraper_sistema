from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import AseguradoraEnum

from .. import dbbase


class AseguradoraModel(dbbase):
    __tablename__ = "aseguradora"

    IDAseguradora:      Mapped[int] = mapped_column(primary_key=True)
    Aseguradora:             Mapped[AseguradoraEnum] = mapped_column(
        SAEnum(AseguradoraEnum, values_callable=lambda x: [e.value for e in x])
    )
    Poliza:          Mapped[int] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint("Aseguradora", "Poliza"),)
