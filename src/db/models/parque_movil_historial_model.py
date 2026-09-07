from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, SmallInteger, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import (
    EstadoHabilitacionEnum,
    TipoCombustibleEnum,
    TipoHabilitacionEnum,
    TipoServicioEnum,
    TitularEnum,
)

from .. import dbbase


class ParqueMovilHistorialModel(dbbase):
    __tablename__ = "parque_movil_historial"

    IDParqueMovilHistorial: Mapped[int] = mapped_column(primary_key=True)
    FechaHistorial:         Mapped[date] = mapped_column(Date)
    IDAseguradora:          Mapped[int] = mapped_column(ForeignKey("aseguradora.IDAseguradora"))

    Linea:                  Mapped[int] = mapped_column(SmallInteger)
    Interno:                Mapped[int] = mapped_column(SmallInteger)
    Estado:                 Mapped[str] = mapped_column(String(15))
    KM:                     Mapped[int | None] = mapped_column(Integer)
    Dominio:                Mapped[str | None] = mapped_column(String(7))
    FechaPatentado:         Mapped[date | None] = mapped_column(Date)

    FechaCNRT:              Mapped[date | None] = mapped_column(Date)
    CodCNRT:                Mapped[int | None] = mapped_column(SmallInteger)
    AñoCNRT:                Mapped[int | None] = mapped_column(SmallInteger)
    HabilitacionCNRT:       Mapped[str | None] = mapped_column(String(40))

    Asientos:               Mapped[int] = mapped_column(SmallInteger)
    TipoServicio:           Mapped[TipoServicioEnum | None]    = mapped_column(SAEnum(TipoServicioEnum, values_callable=lambda x: [e.value for e in x]))
    TipoCombustible:        Mapped[TipoCombustibleEnum | None] = mapped_column(SAEnum(TipoCombustibleEnum, values_callable=lambda x: [e.value for e in x]))
    AireAcond:              Mapped[bool] = mapped_column(Boolean)
    Prendado:               Mapped[bool] = mapped_column(Boolean)
    Titular:                Mapped[TitularEnum | None] = mapped_column(SAEnum(TitularEnum, values_callable=lambda x: [e.value for e in x]))

    Carroceria:             Mapped[str | None] = mapped_column(String(30))

    IDChasis:               Mapped[int | None] = mapped_column(ForeignKey("chasis_modelo.IDChasisModelo"))
    ChasisCod:              Mapped[str | None] = mapped_column(String(60))
    ChasisAño:              Mapped[int | None] = mapped_column(SmallInteger)

    IDMotor:                Mapped[int | None] = mapped_column(ForeignKey("motor_modelo.IDMotorModelo"))
    MotorCod:               Mapped[str | None] = mapped_column(String(60))

    Actual:                 Mapped[date | None] = mapped_column(Date)
    Anterior:               Mapped[date | None] = mapped_column(Date)
    Observacion:            Mapped[str | None] = mapped_column(String(200))
    TipoHabilitacion:       Mapped[TipoHabilitacionEnum | None] = mapped_column(SAEnum(TipoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
    EstadoHabilitacion:     Mapped[EstadoHabilitacionEnum | None] = mapped_column(SAEnum(EstadoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
