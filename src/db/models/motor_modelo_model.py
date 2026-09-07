from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .. import dbbase


class MotorModeloModel(dbbase):
    __tablename__ = "motor_modelo"

    IDMotorModelo:     Mapped[int] = mapped_column(primary_key=True)
    IDMotorMarca:      Mapped[int] = mapped_column(ForeignKey("motor_marca.IDMotorMarca"))
    MotorModelo:       Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("IDMotorMarca", "MotorModelo"),)
