from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class ChasisModeloModel(dbbase):
    __tablename__ = "chasis_modelo"

    IDChasisModelo:     Mapped[int] = mapped_column(primary_key=True)
    IDChasisMarca:      Mapped[int] = mapped_column(ForeignKey("chasis_marca.IDChasisMarca"))
    ChasisModelo:       Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("IDChasisMarca", "ChasisModelo"),)
