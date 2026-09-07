import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pytz import timezone

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _req(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {key}")
    return value


DB_USER = _req("DB_USER")
DB_PASSWORD = _req("DB_PASSWORD")
DB_PORT = _req("DB_PORT")
DB_NAME = _req("DB_NAME")
DB_HOST = _req("DB_HOST")
DB_SSL_MODE = _req("DB_SSL_MODE")
DB_CA = BASE_DIR / "ca.pem"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4&ssl_ca={DB_CA}"

arg_tz = timezone("America/Argentina/Buenos_Aires")

RUTA_PROGRAMA   = Path(r"C:\SISVFP")
RUTA_SERVER     = Path(r"\\sistema01\SANANTONIO")

RUTA_SERVER_STOCK   = RUTA_SERVER / "SANANTON" / "REPUESTO" / "STOCK"
RUTA_SERVER_AGUSTIN = RUTA_SERVER / "NUDO" / "Agustin"
RUTA_SERVER_DELDIA  = RUTA_SERVER / "DSKNAV" / "DELDIA.DBF"

RUTA_SERVER_FICANT      = RUTA_SERVER_STOCK / "FICANT.DBF"
RUTA_SERVER_FICANT1     = RUTA_SERVER_STOCK / "FICANT1.DBF"
RUTA_SERVER_FICART      = RUTA_SERVER_STOCK / "FICART.DBF"
RUTA_SERVER_ARTSTK      = RUTA_SERVER_STOCK / "ARTSTK.DBF"
RUTA_SERVER_FAMSTK      = RUTA_SERVER_STOCK / "FAMSTK.DBF"
RUTA_SERVER_TABLASV     = RUTA_SERVER_STOCK / "TABLASV.DBF"
RUTA_SERVER_DEPSTK      = RUTA_SERVER_STOCK / "DEPSTK.DBF"
RUTA_SERVER_LISTSISA    = RUTA_SERVER_STOCK / "LISTSISA.DBF"
RUTA_SERVER_EMPRESA     = RUTA_SERVER_STOCK / "EMPRESA.DBF"
RUTA_SERVER_BORGAR      = RUTA_SERVER_STOCK / "BORGAR.DBF"
RUTA_SERVER_SITUVFP     = RUTA_SERVER_STOCK / "SITUVFP.DBF"
RUTA_SERVER_PROVE       = RUTA_SERVER_STOCK / "PROVE.DBF"

PAGE_LOGIN = "https://sistemasanantonio.com.ar/san_antonio/login.aspx"
PAGE_PARQUE_MOVIL = (
    "https://sistemasanantonio.com.ar/san_antonio/mod_flota/Grilla_ParqueMovil.aspx"
)

IGNORAR = {"$recycle.bin", "system volume information", ".git", "backup", "temp", "tmp"}

TITULO_LOGIN = "STOCK - Inicio de Sesión"
TITULO_PRINCIPAL = r"Sistemas San Antonio - Stock.*"
TITULO_GUARDAR = "Crear Archivo de Excel"


TODAY = datetime.now(arg_tz)
TODAY_EXISTENCIA = TODAY.strftime("%Y-%m-%d")
TODAY_NAME = TODAY.strftime("%d/%m/%Y").replace("/", "-")
TODAY_MINUS_ONE = (TODAY - timedelta(days=1)).strftime("%d/%m/%Y")

COORDS_EXCEL_BTTN: tuple[int, int] = (431, 193)

TAB = "{TAB}"
ENTER = "{ENTER}"
ENTER2 = "{ENTER 2}"
DOWN_ARR = "{DOWN}"
UP_ARR = "{UP}"

SORT_COLS = ["Familia", "Articulo"]

DF_FICHA = [
    "FICFAM",
    "FICART",
    "FICFEC",
    "FICDEP",
    "FICMOV",
    "FICCAN",
    "FICUNI",
    "FICUSU",
    "FICTRA",
]

DF_EXISTENCIA = ["ARTFAM", "ARTNUM", "ARTNOM", "ARTUNI", "ARTSTK"]




RENAME_COLS_FICHA = {
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

RENAME_COLS_EXISTENCIA = {
    "ARTFAM": "Familia",
    "ARTNUM": "Articulo",
    "ARTNOM": "Nombre",
    "ARTUNI": "Unidad",
    "ARTSTK": "Stock",
}

RENAME_COLS_PARQUE = {
    "Linea": "Linea",
    "Interno": "Interno",
    "Estado": "Estado",
    "Kilometraje": "KM",
    "Dominio": "Dominio",
    "Fecha alta CNRT/prov": "FechaCNRT",
    "Carroceria": "Carroceria",
    "CNRT Nº Parque": "CodCNRT",
    "CNRT Año": "AñoCNRT",
    "Exp. hab. CNRT": "HabilitacionCNRT",
    "Asientos": "Asientos",
    "Tipo Servicio": "TipoServicio",
    "Tipo de Combustible": "TipoCombustible",
    "Aire Acondicionado": "AireAcond",
    "Prendado": "Prendado",
    "Titular": "Titular",
    "Fecha patentado": "FechaPatentado",
    "Chasis Marca": "ChasisMarca",
    "Chasis Modelo": "ChasisModelo",
    "Chasis N°": "ChasisCod",
    "Chasis Año": "ChasisAño",
    "Motor Marca": "MotorMarca",
    "Motor modelo": "MotorModelo",
    "Motor N° de serie": "MotorCod",
    "Aseguradora": "Aseguradora",
    "Poliza N°": "Poliza",
    "Actual": "Actual",
    "Anterior": "Anterior",
    "Observación": "Observacion",
    "Hab. Tipo": "TipoHabilitacion",
    "Hab. Estado": "EstadoHabilitacion",
}

RENAME_MOV = {
    "COM": "Entrada",
    "FAL": "Entrada",
    "DEU": "Entrada",
    "TRA": "Entrada",
    "AJ+": "Entrada",
    "DES": "Salida",
    "SOB": "Salida",
    "DEC": "Salida",
    "DEG": "Salida",
    "TRD": "Salida",
    "AJ-": "Salida",
}

RENAME_UNIDADES = {
    "LATAS": "LATAS",
    "LITROS": "LITROS",
    "L": "LITROS",
    "LITRO": "LITROS",
    "X LITRO": "LITROS",
    "UNIDAD": "UNIDAD",
    "AEROSOL": "UNIDAD",
    "U": "UNIDAD",
    "1": "UNIDAD",
    "S": "UNIDAD",
    "C/U": "UNIDAD",
    "": None,
    "R": None,
    "0": None,
    "NN": None,
    "SS": None,
    "SSS": None,
    "SSSSSSS": None,
    "KILO": "KILOGRAMOS",
    "KILOGRAMOS": "KILOGRAMOS",
    "KG": "KILOGRAMOS",
    "METRO": "METROS",
    "METROS": "METROS",
    "MTS": "METROS",
    "X METRO": "METROS",
    "JUEGO": "JUEGO",
    "JGO X RUEDA": "JUEGO X RUEDA",
    "X2 MITADES": "JUEGO X 2",
    "JUEGO X 2": "JUEGO X 2",
    "PAR": "JUEGO X 2",
    "3": "JUEGO X 3",
    "JGO X 6": "JUEGO X 6",
    "JUEGO X 7": "JUEGO X 7",
}

RENAME_TITULAR = {
    "": np.nan,
    "DOTA SA": "DOTA S.A.",
    "DOTA  SA": "DOTA S.A.",
    "DOTA S.A. DE TRANSP AUTOMOTOR": "DOTA S.A.",
    "DOTA S.A.": "DOTA S.A.",
    "DOTA SATA": "DOTA S.A.",
    "DOTA S.A": "DOTA S.A.",
    "DOTA": "DOTA S.A.",
    "DOTA.SA": "DOTA S.A.",
    "DOTAS.A": "DOTA S.A.",
    "DOTASATA": "DOTA S.A.",
    "LVEGA": "LOPE DE VEGA",
    "LOPE DE VEGA": "LOPE DE VEGA",
    "TRANSPORTES LOPE DE VEGA": "LOPE DE VEGA",
    "TRANSPORTES LOPE DE VEGA SACI": "LOPE DE VEGA",
    "TRANSFPORTES LOPE DE BEGA": "LOPE DE VEGA",
    "TRASPORTES RIO GRANDE SOCIEDAD ANONIMA COMERCIAL INDUSTRIAL Y FINANCIERA": "RIO GRANDE",
    "RGDE": "RIO GRANDE",
    "RIO GRANDE": "RIO GRANDE",
    "TRABSPORTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRANSPRTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRAANPORTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRANSPORTES RI GRANDE SACIF": "RIO GRANDE",
    "TRANSORTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRASNPORTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRANSPORTES RIO GRANDE SACIF": "RIO GRANDE",
    "TRANSPORTES  RIO GRANDE SACIF": "RIO GRANDE",
    "RIOGRANDE": "RIO GRANDE",
    "RGRANDE": "RIO GRANDE",
    "RIOGARNDE": "RIO GRANDE",
    "TRANSPORTES RIO GRANDE": "RIO GRANDE",
    "LARRAZABAL": "LARRAZABAL C.I.S.A.",
    "TRANSPORTE LARRAZABAL CISA": "LARRAZABAL C.I.S.A.",
    "LARRAZABAL C.I.S.A.": "LARRAZABAL C.I.S.A.",
    "LARRAZABAL C.I.S.A": "LARRAZABAL C.I.S.A.",
    "TRANSPORTE LARRAZABAL": "LARRAZABAL C.I.S.A.",
    "TRANSPORTES LARRAZABAL CISA": "LARRAZABAL C.I.S.A.",
    "TRANSPORTES LARRAZABAL": "LARRAZABAL C.I.S.A.",
    "TRNSPORTES LARRAZABAL": "LARRAZABAL C.I.S.A.",
    "TRANSPORTES  LARRAZABAL CISA": "LARRAZABAL C.I.S.A.",
    "TRANSPORTE LAARRAZABAL CISA": "LARRAZABAL C.I.S.A.",
    "LARRAZABAl": "LARRAZABAL C.I.S.A.",
    "TGUIDO": "TOMAS GUIDO",
    "TOMAS GUIDO": "TOMAS GUIDO",
    "GRAL TOMAS GUIDO SACIF": "TOMAS GUIDO",
    "GRAL TOMAS GUIDO": "TOMAS GUIDO",
    "T.GUIDO": "TOMAS GUIDO",
    "ROCARAZA SA": "ROCARAZA S.A.",
    "ROCARAZA": "ROCARAZA S.A.",
    "rocaraza": "ROCARAZA S.A.",
    "ROCA": "GENERAL ROCA S.A.",
    "gral roca": "GENERAL ROCA S.A.",
    "GRAL ROCA": "GENERAL ROCA S.A.",
    "GRAL ROCA SA": "GENERAL ROCA S.A.",
    "GENERALROCA": "GENERAL ROCA S.A.",
    "GRALROCA": "GENERAL ROCA S.A.",
    "GENERAL ROCA": "GENERAL ROCA S.A.",
    "EMP DE TRANSP TTE GRAL ROCA SA": "GENERAL ROCA S.A.",
    "LOS CONSTITUYENTES S.A.T.": "LOS CONSTITUYENTES S.A.T.",
    "LOS CONSTITUYENTES SAT": "LOS CONSTITUYENTES S.A.T.",
    "EL PUENTE": "EL PUENTE",
    "TURISMO EL PUENTE": "TURISMO EL PUENTE",
    "TARSA": "TARSA",
    "TRANSPORTES AUTOMOTORES RIACHUELO SA": "TARSA",
    "CUSA": "CUSA",
    "TRANSPORTES ATLANTIDA SAC": "CUSA",
    "TRANSPORTES ATLANDIDA SAC": "CUSA",
    "TRANSPORTES ATLANTIDA SAC /CUSA": "CUSA",
    "COLECTIVEROS UNIDOS SACIF": "CUSA",
    "COLECTIVEROS UNIDOS S A C I Y F": "CUSA",
    "COLECTIVEROS UNIDOS SA": "CUSA",
    "COLECTIVEROS UNIDOS SAF": "CUSA",
    "COLECTIVEROS UNIDOS SAIF": "CUSA",
    "EXPRESO SAN ISIDRO S.A.": "ESISA",
    "EXPRESO SAN ISIDRO SATCIFI": "ESISA",
    "EXPRESO SAN ISIDRO SACIF": "ESISA",
    "EXPRESO SAN ISIDRO": "ESISA",
    "EXPRESO SAN  ISIDRO": "ESISA",
    "E.ISIDRO": "ESISA",
    "ESISA": "ESISA",
    "ETAPSA": "ETAPSA",
    "EMPRESARIOS TRANSPORTE AUTOMOTOR DE PASAJEROS": "ETAPSA",
    "EMPRESARIOS DE TRANSPORTE DE PASAJEROS": "ETAPSA",
    "EMPRESARIOS TRANSPORTE AUTOMOTOR": "ETAPSA",
    "NUDO": "NUDO S.A.",
    "NUDO  SA": "NUDO S.A.",
    "NUDO SA": "NUDO S.A.",
    "MONSA": "MONSA",
    "MICROOMNIBUS NORTE": "MONSA",
    "MONSA/ SE USA COMO BOMBERO": "MONSA",
    "MONSA SA": "MONSA",
    "MICROMNIBUS NORTE": "MONSA",
    "MICROOMNIBUS NORTE SA": "MONSA",
    "MICRO OMNIBUS NORTE S.A.": "MONSA",
    "TODO BUS": "TODO BUS",
    "San Vicente": "SAN VICENTE",
    "SAN VICENTE": "SAN VICENTE",
    "SAN VICENTE AUXILIO": "SAN VICENTE",
    "EMPRESA SAN VICENTE SAT": "SAN VICENTE",
    "EMPRESA SAN VICENTE": "SAN VICENTE",
    "SAN VICENTE SAT": "SAN VICENTE",
    "SANVICENTE": "SAN VICENTE",
    "EMPRESA SAN VICENTE S.A.T": "SAN VICENTE",
    "EMPRESA SAN VICENTE S.T.A": "SAN VICENTE",
    "MOA": "MOA",
    "MICRO OMNIBUS AVENIDA S.A.": "MOA",
    "MICRO OMNIBUS AVENIDA S.A": "MOA",
    "BENITEZ": "BENITEZ",
    "MEGACAR": "MEGACAR",
    "12DEOCTUBRE": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "12 DE OCTUBRE": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "TRANSPORTES  12 DE OCTUBRE SA": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "TRANSPORTES AUTOMOTORES 12 DE OCTUBRE SA": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "TRANSPORTES 12 DE OCTUBRE SA": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "TRANSPORTES AUTOMOTORES 12 DE OCTUBRE": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "TRANSPORTES AUT 12 DE OCTUBRE S A": "TRANSPORTES 12 DE OCTUBRE S.A.",
    "EL RECREO": "EL RECREO",
    "ATLANTIDA": "ATLANTIDA",
    "TRANSPORTES ATLANTIDA S.A.C.": "ATLANTIDA",
    "TRANSPORTES ATLANTIDA SA": "ATLANTIDA",
    "TRASNPORTES ATLATINDA SAC": "ATLANTIDA",
    "ATLANTIDA SAC": "ATLANTIDA",
    "TRANSPORTES ATLANTIDA": "ATLANTIDA",
    "TRASNPORTES ATLANTIDA SAC": "ATLANTIDA",
    "TRANSPORTES ATALNTIDA SAC": "ATLANTIDA",
    "TRANSPOTES ATLANTIDA SAC": "ATLANTIDA",
    "TRANSPORETES ATLANTIDA SAC": "ATLANTIDA",
    "TRANSPORTES AV. BERNARDO ADER SA": "TABA",
    "TRANSPORTES AV BERNARDO ADER S.A.": "TABA",
    "TRANSPORTES AV. BERNADO ADER SA": "TABA",
    "TRANSPORTES AVENIDA BERNARDO ADER SA": "TABA",
    "TRANSPORTES AV BERNARDO ADER S03.A.": "TABA",
    "TRANSP. AV. BERNARDO ADER SA": "TABA",
    "MARY GO": "MARY GO",
    "ANDRADE": "ANDRADE",
}

TIPOS_DATOS_COLS = {
    "Deposito": "UInt64",
    "TipoMov": "category",
    "Cantidad": "Float32",
    "PrecioUnitario": "Float32",
    "Usuario": "string[pyarrow]",
    "DepositoTransfer": "UInt64",
}

TIPOS_DEPOS_COLS = {"Deposito": "category", "DepositoTransfer": "category"}

TIPOS_DATOS_PARQUE = {
    "Linea": "UInt16",
    "Interno": "UInt16",
    "Estado": "category",
    "KM": "UInt64",
    "Dominio": "string[pyarrow]",
    "FechaCNRT": "datetime64[ns]",
    "Carroceria": "category",
    "CodCNRT": "UInt16",
    "AñoCNRT": "UInt16",
    "HabilitacionCNRT": "string[pyarrow]",
    "Asientos": "UInt16",
    "TipoServicio": "category",
    "TipoCombustible": "category",
    "AireAcond": "bool",
    "Prendado": "bool",
    "Titular": "string[pyarrow]",
    "FechaPatentado": "datetime64[ns]",
    "ChasisMarca": "category",
    "ChasisModelo": "category",
    "ChasisCod": "string[pyarrow]",
    "ChasisAño": "UInt16",
    "MotorMarca": "category",
    "MotorModelo": "category",
    "MotorCod": "string[pyarrow]",
    "Aseguradora": "category",
    "Poliza": "category",
    "Actual": "datetime64[ns]",
    "Anterior": "datetime64[ns]",
    "Observacion": "category",
    "TipoHabilitacion": "category",
    "EstadoHabilitacion": "category",
}


SI_NO = {"si": True, "sí": True, "no": False}
