import re
from collections import Counter
from pathlib import Path

import pandas as pd

from src.core.conjuntos import CONJUNTOS_REPUESTOS
from src.core.constants import CARACTERES_ERRONEOS, REGLAS_TIPO_DURACION
from src.core.sinonimos import SINONIMOS

# ------------------------- LOCAL -------------------------

REGEX_USER_C = r"^C\d+$"
REGEX_USER_U = r"^U\d+$"

REGEX_DESCRIP_PATTERN_N = r"(?<=\S)(N°)|(N°)(?=\S)"
REGEX_DESCRIP_REPLACE_N = r" \1\2 "

REGEX_DESCRIP_PATTERN_SLASH = r"\b([PCSE])/(?=\S)"
REGEX_DESCRIP_REPLACE_SLASH = r"\1/ "

REGEX_DESCRIP_PATTERN_DOTS = r"\.(?=[A-ZÑ])|(?<!\d)\.(?=\d)"
REGEX_DESCRIP_REPLACE_DOTS = ". "

REGEX_SPACE = r"\s+"
REGEX_DESCRIP_REPLACE_SPACE = " "


def regex_conjuntos():
    KW_CONJUNTO = {kw: c for c, kws in CONJUNTOS_REPUESTOS.items() for kw in kws}

    _conteo = Counter(kw for kws in CONJUNTOS_REPUESTOS.values() for kw in kws)
    _donde = {
        kw: [c for c, kws in CONJUNTOS_REPUESTOS.items() if kw in kws]
        for kw, n in _conteo.items()
        if n > 1
    }
    assert not _donde, f"palabras repetidas: {_donde}"
    assert set(REGLAS_TIPO_DURACION) == set(CONJUNTOS_REPUESTOS), (
        "conjunto sin tipo o tipo sin conjunto"
    )

    patron = "|".join(re.escape(k) for k in sorted(KW_CONJUNTO, key=len, reverse=True))
    regex = rf"(?<![A-Z0-9Ñ])({patron})(?![A-Z0-9Ñ])"

    return {"regex": regex, "kw": KW_CONJUNTO}


def regex_descripcion():
    REEMPLAZOS = {}
    for correcto, variantes in SINONIMOS.items():
        for v in variantes:
            if v in REEMPLAZOS:
                raise ValueError(f"'{v}' está repetida: {REEMPLAZOS[v]} y {correcto}")
            REEMPLAZOS[v] = correcto

    claves = sorted(REEMPLAZOS, key=len, reverse=True)
    PATRON = re.compile(r"(?<!\S)(" + "|".join(map(re.escape, claves)) + r")(?!\S)")

    return {"patron": PATRON, "reemplazos": lambda m: REEMPLAZOS[m.group(1)]}


def regex_filtrar_series(df: pd.DataFrame, tipos: dict[str, list[str]]) -> pd.Series:
    palabra_a_tipo = {
        p.lower(): tipo for tipo, palabras in tipos.items() for p in palabras
    }

    alternativas = sorted(palabra_a_tipo, key=len, reverse=True)
    patron = (
        r"\b("
        + "|".join(re.escape(p).replace(r"\ ", REGEX_SPACE) for p in alternativas)
        + r")"
    )

    encontrada = (
        df["Descripcion"]
        .str.extract(patron, flags=re.IGNORECASE, expand=False)
        .str.lower()
        .str.replace(REGEX_SPACE, REGEX_DESCRIP_REPLACE_SPACE, regex=True)
    )

    return encontrada.map(palabra_a_tipo)


REPLACE_USERS = {"C": "", "U": "", "c": "", "u": ""}
REPLACE_CONDICION = {"NUEVO": "", "REPARADO": "", '"CRITICO"': "", '"CRITICA"': ""}

regex_descrip = regex_descripcion()

REEMPLAZOS_DESCRIP = {
    **CARACTERES_ERRONEOS,
    **REPLACE_CONDICION,
    REGEX_DESCRIP_PATTERN_N: REGEX_DESCRIP_REPLACE_N,
    REGEX_DESCRIP_PATTERN_SLASH: REGEX_DESCRIP_REPLACE_SLASH,
    REGEX_DESCRIP_PATTERN_DOTS: REGEX_DESCRIP_REPLACE_DOTS,
    regex_descrip["patron"]: regex_descrip["reemplazos"],
}


FILTER_DESCRIP_CRITICO = "CRITICO|CRITICA|CRITICOS|CRITICAS"

REPUESTOS_CLAVES_COLS = ["Familia", "Articulo"]
REPUESTOS_COLS = ["Familia", "Articulo", "Nombre"]
REPUESTOS_PK_COLS = tuple(REPUESTOS_CLAVES_COLS)
REPUESTOS_UNIDADES_COLS = [
    "Familia",
    "Articulo",
    "Unidades",
    "FechaDesde",
    "FechaHasta",
]


CONDICION_REPUESTOS = {
    "NUEVO": ["NVO", "NUEVO", "NUEVA", "NVA"],
    "REPARADO": ["REP", "REPA", "REPARADO", "REPARADA"],
}


# ------------------------- WEB -------------------------
USUARIO = "sergiop.dota@gmail.com"
PASSWORD = "123*"

URL_PARQUE = "http://100.72.69.144:8080/parque_historial.xlsx"
PATH_PARQUE = Path("/mnt/HDD/data_scraper_sistema/descargas/parque_movil.xlsx")

PARQUE_HISTORIAL_COLS = ["Dominio", "FechaHistorial"]
VIGENCIA_COLS = ["Interno", "Dominio", "FechaDesde", "FechaHasta", "FechaPatentado"]
FECHAS_COLS = ["FechaDesde", "FechaHasta", "FechaPatentado"]

ASEGURADORA_COLS = ["Aseguradora", "Poliza"]

CHASIS_COLS = ["ChasisMarca", "ChasisModelo"]
CHASIS_FK_COLS = ["IDChasisMarca", "ChasisModelo"]

MOTOR_COLS = ["MotorMarca", "MotorModelo"]
MOTOR_FK_COLS = ["IDMotorMarca", "MotorModelo"]

NUMERIC_COLS = ["Poliza", "KM", "CodCNRT"]
