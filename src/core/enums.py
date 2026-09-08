from enum import Enum, auto
from pathlib import Path

from strenum import LowercaseStrEnum


class RutasServidor:
    def __init__(self, ruta_base: str):
        self.base = Path(ruta_base)

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


class CabecerasPathEnum(Enum):
    MEGABUS = ("Megabus", RutasServidor(r"\\sistema01\SANANTONIO\SANANTON\REPUESTO\STOCK"))
    POMPEYA = ("Pompeya", RutasServidor(r""))
    LA_NORIA = ("La Noria", RutasServidor(r"\\SISTEMA02\Repuestos\SISSSA"))
    BONZI = ("Bonzi", RutasServidor(r""))
    EVA_PERON = ("Eva Peron", RutasServidor(r""))
    MEDINA = ("Medina", RutasServidor(r""))
    CUSA = ("Cusa", RutasServidor(r""))
    ETAPSA = ("Etapsa", RutasServidor(r""))
    ESISA = ("Esisa", RutasServidor(r""))
    LUJAN = ("Lujan", RutasServidor(r""))
    MASCHWITZ = ("Maschwitz", RutasServidor(r""))
    BARRACAS = ("Barracas", RutasServidor(r""))
    PILAR = ("Pilar", RutasServidor(r""))
    CONSTITUYENTES = ("Constituyentes", RutasServidor(r""))
    LONGCHAMPS = ("Longchamps", RutasServidor(r""))
    TG_LANUS = ("TG Lanus", RutasServidor(r""))
    TG_CALZADA = ("TG Calzada", RutasServidor(r""))
    TARSA_CIUDADELA = ("Tarsa Ciudadela", RutasServidor(r""))
    TARSA_LANUS = ("Tarsa Lanus", RutasServidor(r""))
    TARSA_134 = ("Tarsa 134", RutasServidor(r""))
    EL_PUENTE = ("El Puente", RutasServidor(r""))


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
