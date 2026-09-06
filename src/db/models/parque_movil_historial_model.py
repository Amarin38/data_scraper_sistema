from datetime import date

from sqlalchemy import Boolean, Date, Integer, SmallInteger, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import TitularEnum, EstadoHabilitacionEnum, TipoHabilitacionEnum

from .. import dbbase


class ParqueMovilHistorialModel(dbbase):
    __tablename__ = "parque_movil_historial"

    IDParqueMovilHistorial: Mapped[int] = mapped_column(primary_key=True)
    Dominio:                Mapped[str | None] = mapped_column(String(7))
    Linea:                  Mapped[int] = mapped_column(SmallInteger)
    Interno:                Mapped[int] = mapped_column(SmallInteger)
    InternoHistorial:       Mapped[int | None] = mapped_column(SmallInteger)
    Estado:                 Mapped[str | None] = mapped_column(String(15))
    FechaHistorial:         Mapped[date | None] = mapped_column(Date)
    Usuario:                Mapped[str | None] = mapped_column(String(30))
    Observaciones:          Mapped[str | None] = mapped_column(String(150))
    Año:                    Mapped[int | None] = mapped_column(SmallInteger)
    Parque:                 Mapped[int | None] = mapped_column(SmallInteger)
    ChasisMarca:            Mapped[str | None] = mapped_column(String(30))
    ChasisModelo:           Mapped[str | None] = mapped_column(String(50))
    MotorMarca:             Mapped[str] = mapped_column(String(80))
    MotorCod:               Mapped[str | None] = mapped_column(String(60))
    ChasisCod:              Mapped[str | None] = mapped_column(String(60))
    KM:                     Mapped[int] = mapped_column(Integer)
    Asientos:               Mapped[int] = mapped_column(SmallInteger)
    Carroceria:             Mapped[str | None] = mapped_column(String(30))
    Titular:                Mapped[TitularEnum | None] = mapped_column(SAEnum(TitularEnum, values_callable=lambda x: [e.value for e in x]))
    Proveedor:              Mapped[str | None] = mapped_column(String(30))
    FechaCompra:            Mapped[date | None] = mapped_column(Date)
    TipoCombustible:        Mapped[str | None] = mapped_column(String(15))
    TipoServicio:           Mapped[str | None] = mapped_column(String(20))
    Poliza:                 Mapped[str | None] = mapped_column(String(7))
    Aseguradora:            Mapped[str | None] = mapped_column(String(20))
    VigenciaPolizaDesde:    Mapped[date | None] = mapped_column(Date)
    VigenciaPolizaHasta:    Mapped[date | None] = mapped_column(Date)
    TipoHabilitacion:       Mapped[TipoHabilitacionEnum | None] = mapped_column(SAEnum(TipoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
    EstadoHabilitacion:     Mapped[EstadoHabilitacionEnum | None] = mapped_column(SAEnum(EstadoHabilitacionEnum, values_callable=lambda x: [e.value for e in x]))
    Habilitacion:           Mapped[str | None] = mapped_column(String(10))
    Prendado:               Mapped[bool] = mapped_column(Boolean)
    OfertaLibre:            Mapped[bool] = mapped_column(Boolean)
