import logging
from enum import Enum
from pathlib import Path

from src.core.constants import PATH_CABECERAS
from src.core.enums import CabecerasEnum

logger = logging.getLogger(__name__)


class RutasServidor:
    def __init__(self, ruta_base: Path):
        self.base = ruta_base

        self.FICANT = self.base / "FICANT.DBF"
        self.FICANT1 = self.base / "FICANT1.DBF"
        self.FICART = self.base / "FICART.DBF"
        self.ARTSTK = self.base / "ARTSTK.DBF"

    def obtener_archivos(self) -> list:
        rutas = [self.FICANT, self.FICANT1, self.FICART]
        existentes = []

        for r in rutas:
            if r.exists():
                existentes.append(r)
            else:
                logger.warning("falta %s, se omite", r)

        return existentes


class CabecerasPathEnum(Enum):
    MEGABUS = (CabecerasEnum.MEGABUS, RutasServidor(PATH_CABECERAS / "megabus"))
    POMPEYA = (CabecerasEnum.POMPEYA, RutasServidor(PATH_CABECERAS / "pompeya"))
    LA_NORIA = (CabecerasEnum.LA_NORIA, RutasServidor(PATH_CABECERAS / "la_noria"))
    BONZI = (CabecerasEnum.BONZI, RutasServidor(PATH_CABECERAS / "bonzi"))
    EVA_PERON = (CabecerasEnum.EVA_PERON, RutasServidor(PATH_CABECERAS / "eva_peron"))
    MEDINA = (CabecerasEnum.MEDINA, RutasServidor(PATH_CABECERAS / "medina"))
    CUSA = (CabecerasEnum.CUSA, RutasServidor(PATH_CABECERAS / "cusa"))
    ETAPSA = (CabecerasEnum.ETAPSA, RutasServidor(PATH_CABECERAS / "etapsa"))
    ESISA = (CabecerasEnum.ESISA, RutasServidor(PATH_CABECERAS / "esisa"))
    LUJAN = (CabecerasEnum.LUJAN, RutasServidor(PATH_CABECERAS / "lujan"))
    MASCHWITZ = (CabecerasEnum.MASCHWITZ, RutasServidor(PATH_CABECERAS / "maschwitz"))
    BARRACAS = (CabecerasEnum.BARRACAS, RutasServidor(PATH_CABECERAS / "barracas"))
    PILAR = (CabecerasEnum.PILAR, RutasServidor(PATH_CABECERAS / "pilar"))
    CONSTITUYENTES = (
        CabecerasEnum.CONSTITUYENTES,
        RutasServidor(PATH_CABECERAS / "constituyentes"),
    )
    LONGCHAMPS = (
        CabecerasEnum.LONGCHAMPS,
        RutasServidor(PATH_CABECERAS / "longchamps"),
    )
    SAN_VICENTE = (
        CabecerasEnum.SAN_VICENTE,
        RutasServidor(PATH_CABECERAS / "san_vicente"),
    )
    TG_LANUS = (CabecerasEnum.TG_LANUS, RutasServidor(PATH_CABECERAS / "tg_lanus"))
    TG_CALZADA = (
        CabecerasEnum.TG_CALZADA,
        RutasServidor(PATH_CABECERAS / "tg_calzada"),
    )
    TARSA_CIUDADELA = (
        CabecerasEnum.TARSA_CIUDADELA,
        RutasServidor(PATH_CABECERAS / "tarsa_ciudadela"),
    )
    TARSA_LANUS = (
        CabecerasEnum.TARSA_LANUS,
        RutasServidor(PATH_CABECERAS / "tarsa_lanus"),
    )
    TARSA_134 = (CabecerasEnum.TARSA_134, RutasServidor(PATH_CABECERAS / "tarsa_134"))
    EL_PUENTE = (CabecerasEnum.EL_PUENTE, RutasServidor(PATH_CABECERAS / "el_puente"))


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
