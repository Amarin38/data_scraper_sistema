from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class ChasisMarcaModel(dbbase):
    __tablename__ = "chasis_marca"

    IDChasisMarca:      Mapped[int] = mapped_column(primary_key=True)
    ChasisMarca:        Mapped[str] = mapped_column(String(25))

    __table_args__ = (UniqueConstraint("ChasisMarca"),)
