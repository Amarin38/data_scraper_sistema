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


class ParqueMovilModel(dbbase):
    __tablename__ = "parque_movil"

    IDParqueMovil:      Mapped[int] = mapped_column(primary_key=True)
    IDAseguradora:      Mapped[int] = mapped_column(ForeignKey("aseguradora.IDAseguradora"))
    Linea:              Mapped[int] = mapped_column(SmallInteger)
    Interno:            Mapped[int] = mapped_column(SmallInteger)
    Estado:             Mapped[str] = mapped_column(String(15))
    KM:                 Mapped[int] = mapped_column(Integer)
    Dominio:            Mapped[str | None] = mapped_column(String(7))
    FechaCNRT:          Mapped[date | None] = mapped_column(Date)
    Carroceria:         Mapped[str | None] = mapped_column(String(30))
    CodCNRT:            Mapped[int | None] = mapped_column(SmallInteger)
    AñoCNRT:            Mapped[int | None] = mapped_column(SmallInteger)
    HabilitacionCNRT:   Mapped[str | None] = mapped_column(String(40))
    Asientos:           Mapped[int] = mapped_column(SmallInteger)
    TipoServicio:       Mapped[TipoServicioEnum | None]    = mapped_column(SAEnum(TipoServicioEnum, values_callable=lambda x: [e.value for e in x]))
    TipoCombustible:    Mapped[TipoCombustibleEnum | None] = mapped_column(SAEnum(TipoCombustibleEnum, values_callable=lambda x: [e.value for e in x]))
    AireAcond:          Mapped[bool] = mapped_column(Boolean)
    Prendado:           Mapped[bool] = mapped_column(Boolean)
    Titular:            Mapped[TitularEnum | None] = mapped_column(SAEnum(TitularEnum, values_callable=lambda x: [e.value for e in x]))
    Proveedor:          Mapped[str | None] = mapped_column(String(30))
    FechaPatentado:     Mapped[date | None] = mapped_column(Date)

    IDChasis:           Mapped[int | None] = mapped_column(ForeignKey("chasis_modelo.IDChasisModelo"))
    ChasisCod:          Mapped[str | None] = mapped_column(String(60))
    ChasisAño:          Mapped[int | None] = mapped_column(SmallInteger)

    # IDMotor:            Mapped[int | None] = mapped_column(ForeignKey("motor_modelo.IDMotorModelo"))
    MotorMarca:         Mapped[str | None] = mapped_column(String(80))
    MotorModelo:        Mapped[str | None] = mapped_column(String(50))
    MotorCod:           Mapped[str | None] = mapped_column(String(60))

    Actual:             Mapped[date | None] = mapped_column(Date)
    Anterior:           Mapped[date | None] = mapped_column(Date)
    Observacion:        Mapped[str | None] = mapped_column(String(200))
    TipoHabilitacion:   Mapped[TipoHabilitacionEnum | None] = mapped_column(SAEnum(TipoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
    EstadoHabilitacion: Mapped[EstadoHabilitacionEnum | None] = mapped_column(SAEnum(EstadoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
    Comprobante:        Mapped[str | None] = mapped_column(String(20))
    Inicio:             Mapped[date | None] = mapped_column(Date)
    Fin:                Mapped[date | None] = mapped_column(Date)
    OfertaLibre:        Mapped[bool] = mapped_column(Boolean)
