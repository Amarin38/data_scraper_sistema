from enum import Enum, auto

from strenum import LowercaseStrEnum


class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()


class TipoScrap(LowercaseStrEnum):
    LOCAL = auto()
    WEB = auto()


class TipoMovEnum(Enum):
    ENTRADA = "Entrada"
    SALIDA = "Salida"
    DEVOLUCION = "Devolucion"
    TRANSFERENCIA = "Transferencia"


class CabecerasEnum(Enum):
    MEGABUS = "Megabus"
    POMPEYA = "Pompeya"
    LA_NORIA = "La Noria"
    BONZI = "Bonzi"
    EVA_PERON = "Eva Peron"
    MEDINA = "Medina"
    CUSA = "Cusa"
    ETAPSA = "Etapsa"
    ESISA = "Esisa"
    LUJAN = "Lujan"
    MASCHWITZ = "Maschwitz"
    BARRACAS = "Barracas"
    PILAR = "Pilar"
    CONSTITUYENTES = "Constituyentes"
    LONGCHAMPS = "Longchamps"
    SAN_VICENTE = "San Vicente"
    TG_LANUS = "TG Lanus"
    TG_CALZADA = "TG Calzada"
    TARSA_CIUDADELA = "Tarsa Ciudadela"
    TARSA_LANUS = "Tarsa Lanus"
    TARSA_134 = "Tarsa 134"
    EL_PUENTE = "El Puente"


class UnidadEnum(Enum):
    LATAS = "LATAS"
    LITROS = "LITROS"
    UNIDAD = "UNIDAD"
    KILOGRAMOS = "KILOGRAMOS"
    METROS = "METROS"
    JUEGO = "JUEGO"
    JUEGO_X_RUEDA = "JUEGO X RUEDA"
    JUEGO_X_2 = "JUEGO X 2"
    JUEGO_X_3 = "JUEGO X 3"
    JUEGO_X_6 = "JUEGO X 6"
    JUEGO_X_7 = "JUEGO X 7"


class TipoServicioEnum(Enum):
    PISO_BAJO = "Piso Bajo"
    COMUN = "Comun"
    MEDIA_DISTANCIA = "Media Distancia"
    ARTICULADO = "Articulado"


class TipoCombustibleEnum(Enum):
    DIESEL = "Diesel"
    GNC = "GNC"
    ELECTRICO = "Eléctrico"


class TitularEnum(Enum):
    DOTA = "DOTA S.A."
    GENERAL_ROCA = "GENERAL ROCA S.A."
    LOPE_DE_VEGA = "LOPE DE VEGA"
    LARRAZABAL = "LARRAZABAL C.I.S.A."
    TARSA = "TARSA"
    TOMAS_GUIDO = "TOMAS GUIDO"
    RIO_GRANDE = "RIO GRANDE"
    ROCARAZA = "ROCARAZA S.A."
    CONSTITUYENTES = "LOS CONSTITUYENTES S.A.T."
    NUDO = "NUDO S.A."
    SAN_VICENTE = "SAN VICENTE"
    MOA = "MOA"
    MONSA = "MONSA"
    CUSA = "CUSA"
    BENITEZ = "BENITEZ"
    EL_PUENTE = "EL PUENTE"
    TURISMO_EL_PUENTE = "TURISMO EL PUENTE"
    MEGACAR = "MEGACAR"
    TODO_BUS = "TODO BUS"
    ETAPSA = "ETAPSA"
    T12_OCTUBRE = "TRANSPORTES 12 DE OCTUBRE S.A."
    ESISA = "ESISA"
    ATLANTIDA = "ATLANTIDA"
    EL_RECREO = "EL RECREO"
    TABA = "TABA"
    MARY_GO = "MARY GO"
    ANDRADE = "ANDRADE"


class TipoHabilitacionEnum(Enum):
    RTO = "RTO"
    VTV = "VTV"


class EstadoHabilitacionEnum(Enum):
    VIGENTE = "VIGENTE"
    VENCIDA = "VENCIDA"
    ACTIVO = "ACTIVO"


class AseguradoraEnum(Enum):
    ARGOS = "ARGOS"


class ModoCargaEnum(LowercaseStrEnum):
    OVERWRITE = auto()
    APPEND = auto()
    UPSERT = auto()


class TipoCompute(LowercaseStrEnum):
    DURACION_REPUESTOS = auto()
    PREVISION = auto()
    INDICE_CONSUMO = auto()
    CONTEO_STOCK = auto()


class TipoUsuarioEnum(Enum):
    COCHE = "Coche"
    CABECERA = "Cabecera"
    USUARIO = "Usuario"


class TipoDuracionEnum(Enum):
    CONSUMIBLE = "Consumible"
    INSUMO = "Insumo menor"
    DESGASTE = "Desgaste"
    PREVENTIVO = "Preventivo"
    EVENTUAL = "Eventual"

    @classmethod
    def obtener_con_duracion(cls) -> tuple[TipoDuracionEnum, ...]:
        return (cls.DESGASTE, cls.PREVENTIVO, cls.EVENTUAL)


class TipoPrevisionEnum(Enum):
    PROMEDIO = "Promedio"
    CROSTON = "Croston"
    EXPONENCIAL = "Exponencial"


class FormatoEnum(LowercaseStrEnum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
