from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class MotorMarcaModel(dbbase):
    __tablename__ = "motor_marca"

    IDMotorMarca:      Mapped[int] = mapped_column(primary_key=True)
    MotorMarca:        Mapped[str] = mapped_column(String(25))

    __table_args__ = (UniqueConstraint("MotorMarca"),)
