from pathlib import Path
from datetime import datetime
from enum import auto
from strenum import LowercaseStrEnum

RUTA_PROGRAMA = Path(r"C:\SISVFP")
RUTA_ARCHIVOS = Path(r"C:\Users\repuestos01\Documents\datos_mensuales")
TODAY = datetime.now()
COORDS_EXCEL_BTTN: tuple[int, int] = (431, 193)
TAB = "{TAB}"
ENTER = "{ENTER}"
ENTER2 = "{ENTER 2}"
DOWN_ARR = "{DOWN}"
UP_ARR = "{UP}"


class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()
