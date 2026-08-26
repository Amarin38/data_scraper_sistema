from datetime import datetime, date, timedelta
from enum import auto
from pathlib import Path

from pytz import timezone
from strenum import LowercaseStrEnum

arg_tz = timezone("America/Argentina/Buenos_Aires")

RUTA_PROGRAMA = Path(r"C:\SISVFP")
RUTA_ARCHIVOS = Path(r"C:\Users\repuestos01\Documents\datos_mensuales")
RUTA_PARQUE = Path(r"\\sistema01\SANANTONIO\NUDO\Agustin\parques")
RUTA_PARQUE_HISTORIAL = Path(r"\\sistema01\SANANTONIO\NUDO\Agustin\historial_parques")

RUTA_FICHA_STOCK = Path(r"\\sistema01\SANANTONIO\NUDO\Agustin\fichas_stock")

PAGE_LOGIN = "https://sistemasanantonio.com.ar/san_antonio/login.aspx"
PAGE_PARQUE_MOVIL = "https://sistemasanantonio.com.ar/san_antonio/mod_flota/Grilla_ParqueMovil.aspx"


TITULO_LOGIN = "STOCK - Inicio de Sesión"
TITULO_PRINCIPAL = r"Sistemas San Antonio - Stock.*"
TITULO_GUARDAR = "Crear Archivo de Excel"

TODAY = datetime.now(arg_tz).strftime("%d/%m/%Y")
TODAY_MINUS_ONE = (datetime.now(arg_tz) - timedelta(days=1)).strftime("%d/%m/%Y")
COORDS_EXCEL_BTTN: tuple[int, int] = (431, 193)
TAB = "{TAB}"
ENTER = "{ENTER}"
ENTER2 = "{ENTER 2}"
DOWN_ARR = "{DOWN}"
UP_ARR = "{UP}"


class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()
    PARQUE_MOVIL = auto()
