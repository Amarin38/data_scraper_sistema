from datetime import datetime, timedelta
from enum import auto
from pathlib import Path

from pytz import timezone
from strenum import LowercaseStrEnum

arg_tz = timezone("America/Argentina/Buenos_Aires")

RUTA_PROGRAMA = Path(r"C:\SISVFP")
RUTA_SERVER = Path(r"\\sistema01\SANANTONIO")
RUTA_SERVER_STOCK   = RUTA_SERVER / "SANANTON" / "REPUESTO" / "STOCK"
RUTA_SERVER_AGUSTIN = RUTA_SERVER / "NUDO" / "Agustin"

RUTA_SERVER_FICANT  = RUTA_SERVER_STOCK / "FICANT.DBF"
RUTA_SERVER_FICART  = RUTA_SERVER_STOCK / "FICART.DBF"
RUTA_SERVER_FICANT1 = RUTA_SERVER_STOCK / "FICANT1.DBF"
RUTA_SERVER_ARTSTK  = RUTA_SERVER_STOCK / "ARTSTK.DBF"
RUTA_SERVER_TABLASV = RUTA_SERVER_STOCK / "TABLASV.DBF"
RUTA_SERVER_DEPSTK  = RUTA_SERVER_STOCK / "DEPSTK.DBF"

RUTA_PARQUE             = RUTA_SERVER_AGUSTIN / "parques"
RUTA_PARQUE_HISTORIAL   = RUTA_SERVER_AGUSTIN / "historial_parques"
RUTA_FICHA_STOCK        = RUTA_SERVER_AGUSTIN / "fichas_stock"

RUTA_ARCHIVOS = Path(r"C:\Users\repuestos01\Documents\datos_mensuales")

PAGE_LOGIN = "https://sistemasanantonio.com.ar/san_antonio/login.aspx"
PAGE_PARQUE_MOVIL = (
    "https://sistemasanantonio.com.ar/san_antonio/mod_flota/Grilla_ParqueMovil.aspx"
)

IGNORAR = {"$recycle.bin", "system volume information", ".git", "backup", "temp", "tmp"}

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

SORT_COLS = ["FICFAM", "FICART", "FICFEC"]
DROP_COLS = [
    "FICTIP",
    "FICPRO",
    "FICREM",
    "FICFAC",
    "FICIMP",
    "FICTUR",
    "FICGRA",
    "TRANSFE",
    "FICDES",
    "FICRSO",
]

RENAME_COLS = {
    "FICFAM": "Familia",
    "FICART": "Articulo",
    "FICFEC": "FechaMov",
    "FICDEP": "Deposito",
    "FICMOV": "TipoMov",
    "FICCAN": "Cantidad",
    "FICUNI": "PrecioUnitario",
    "FICUSU": "Usuario",
    "FICTRA": "DepositoTransfer",
}

TIPOS_DATOS_COLS = {
    "Familia":"UInt16",
    "Articulo":"UInt32",
    "Deposito": "UInt64",
    "TipoMov": "category",
    "Cantidad": "Float32",
    "PrecioUnitario": "Float32",
    "Usuario": "string[pyarrow]",
    "DepositoTransfer": "UInt64"
}

TIPOS_DEPOS_COLS = {
    "Deposito": "category",
    "DepositoTransfer": "category"
}

RENAME_MOV = {
    "COM": "Entrada",
    "DES": "Salida",
    "DEU": "Devolucion Usuario",
    "DEG": "Devolucion Garantia",
    "TRA": "Transferencia Recibida",
    "TRD": "Transferencia Deposito",
    "INI": "Existencia Inicial"
}

class ListadoExistencias(LowercaseStrEnum):
    FICHA_STOCK = auto()
    EXISTENCIA_STOCK = auto()
    PARQUE_MOVIL = auto()
