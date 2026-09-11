from enum import Enum, auto
from pathlib import Path

from strenum import LowercaseStrEnum

from core.constants import PATH_CABECERAS


class RutasServidor:
    def __init__(self, ruta_base: Path):
        self.base = ruta_base

        self.FICANT = self.base / "FICANT.DBF"
        self.FICANT1 = self.base / "FICANT1.DBF"
        self.FICART = self.base / "FICART.DBF"
        self.ARTSTK = self.base / "ARTSTK.DBF"

    def obtener_archivos(self) -> list:
        return [self.FICANT, self.FICANT1, self.FICART]


class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()


class TipoScrap(LowercaseStrEnum):
    LOCAL = auto()
    WEB = auto()


class TipoMovEnum(Enum):
    ENTRADA = "Entrada"
    SALIDA = "Salida"


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


class CabecerasPathEnum(Enum):
    MEGABUS         = (CabecerasEnum.MEGABUS, RutasServidor(PATH_CABECERAS / "megabus"))
    POMPEYA         = (CabecerasEnum.POMPEYA, RutasServidor(PATH_CABECERAS / "pompeya"))
    LA_NORIA        = (CabecerasEnum.LA_NORIA, RutasServidor(PATH_CABECERAS / "la_noria"))
    BONZI           = (CabecerasEnum.BONZI, RutasServidor(PATH_CABECERAS / "bonzi"))
    EVA_PERON       = (CabecerasEnum.EVA_PERON, RutasServidor(PATH_CABECERAS / "eva_peron"))
    MEDINA          = (CabecerasEnum.MEDINA, RutasServidor(PATH_CABECERAS / "medina"))
    CUSA            = (CabecerasEnum.CUSA, RutasServidor(PATH_CABECERAS / "cusa"))
    ETAPSA          = (CabecerasEnum.ETAPSA, RutasServidor(PATH_CABECERAS / "etapsa"))
    ESISA           = (CabecerasEnum.ESISA, RutasServidor(PATH_CABECERAS / "esisa"))
    LUJAN           = (CabecerasEnum.LUJAN, RutasServidor(PATH_CABECERAS / "lujan"))
    MASCHWITZ       = (CabecerasEnum.MASCHWITZ, RutasServidor(PATH_CABECERAS / "maschwitz"))
    BARRACAS        = (CabecerasEnum.BARRACAS, RutasServidor(PATH_CABECERAS / "barracas"))
    PILAR           = (CabecerasEnum.PILAR, RutasServidor(PATH_CABECERAS / "pilar"))
    CONSTITUYENTES  = (CabecerasEnum.CONSTITUYENTES, RutasServidor(PATH_CABECERAS / "constituyentes"))
    LONGCHAMPS      = (CabecerasEnum.LONGCHAMPS, RutasServidor(PATH_CABECERAS / "longchamps"))
    SAN_VICENTE     = (CabecerasEnum.SAN_VICENTE, RutasServidor(PATH_CABECERAS / "san_vicente"))
    TG_LANUS        = (CabecerasEnum.TG_LANUS, RutasServidor(PATH_CABECERAS / "tg_lanus"))
    TG_CALZADA      = (CabecerasEnum.TG_CALZADA, RutasServidor(PATH_CABECERAS / "tg_calzada"))
    TARSA_CIUDADELA = (CabecerasEnum.TARSA_CIUDADELA, RutasServidor(PATH_CABECERAS / "tarsa_ciudadela"))
    TARSA_LANUS     = (CabecerasEnum.TARSA_LANUS, RutasServidor(PATH_CABECERAS / "tarsa_lanus"))
    TARSA_134       = (CabecerasEnum.TARSA_134, RutasServidor(PATH_CABECERAS / "tarsa_134"))
    EL_PUENTE       = (CabecerasEnum.EL_PUENTE, RutasServidor(PATH_CABECERAS / "el_puente"))


class PathArchivosEnum(Enum):
    MEGABUS = Path(r"\\sistema01\SANANTONIO\SANANTON\REPUESTO\STOCK")
    POMPEYA = ""
    LA_NORIA = ""
    BONZI = ""
    EVA_PERON = ""
    MEDINA = ""
    CUSA = ""
    ETAPSA = ""
    ESISA = ""
    LUJAN = ""
    MASCHWITZ = ""
    BARRACAS = ""
    PILAR = ""
    CONSTITUYENTES = ""
    LONGCHAMPS = ""
    SAN_VICENTE = ""
    TG_LANUS = ""
    TG_CALZADA = ""
    TARSA_CIUDADELA = ""
    TARSA_LANUS = ""
    TARSA_134 = ""
    EL_PUENTE = ""


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
