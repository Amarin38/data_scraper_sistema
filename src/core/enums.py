import enum
from enum import auto

from strenum import LowercaseStrEnum


class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()


class TipoScrap(LowercaseStrEnum):
    LOCAL = auto()
    WEB = auto()


class TipoMovEnum(enum.Enum):
    ENTRADA = "Entrada"
    SALIDA = "Salida"


class CabecerasEnum(enum.Enum):
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
    TG_LANUS = "TG Lanus"
    TG_CALZADA = "TG Calzada"
    TARSA_CIUDADELA = "Tarsa Ciudadela"
    TARSA_LANUS = "Tarsa Lanus"
    TARSA_134 = "Tarsa 134"
    EL_PUENTE = "El Puente"


class UnidadEnum(enum.Enum):
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


class TipoServicioEnum(enum.Enum):
    PISO_BAJO = "Piso Bajo"
    COMUN = "Comun"
    MEDIA_DISTANCIA = "Media Distancia"
    ARTICULADO = "Articulado"


class TipoCombustibleEnum(enum.Enum):
    DIESEL = "Diesel"
    GNC = "GNC"
    ELECTRICO = "Eléctrico"


class TitularEnum(enum.Enum):
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


class TipoHabilitacionEnum(enum.Enum):
    RTO = "RTO"
    VTV = "VTV"


class EstadoHabilitacionEnum(enum.Enum):
    VIGENTE = "VIGENTE"
    VENCIDA = "VENCIDA"
    ACTIVO = "ACTIVO"


class AseguradoraEnum(enum.Enum):
    ARGOS = "ARGOS"
