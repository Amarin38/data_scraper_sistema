import logging
import re
from collections import Counter
from datetime import date
from functools import partial

import pandas as pd
from sqlalchemy.orm import Session

from src.core.conjuntos import CONJUNTOS_REPUESTOS
from src.core.constants import (
    CARACTERES_ERRONEOS,
    CONDICION,
    CONDICION_REPUESTOS,
    DF_EXISTENCIA,
    DF_FICHA,
    REGLAS_TIPO_DURACION,
    REGLAS_UNIDADES_POR_COCHE,
    RENAME_COLS_EXISTENCIA,
    RENAME_COLS_FICHA,
    RENAME_MOV,
    RENAME_REPUESTOS,
    RENAME_UNIDADES,
    REPUESTOS_COLS,
    REPUESTOS_PK_COLS,
    REPUESTOS_SORT_COLS,
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
    TODAY,
    USUARIOS_CABECERA,
)
from src.core.enums import (
    CabecerasEnum,
    ModoCargaEnum,
    TipoUsuarioEnum,
)
from src.core.paths import CabecerasPathEnum
from src.core.sinonimos import SINONIMOS
from src.core.utils import arreglar_fechas, leer
from src.db.models.repuesto_model import RepuestoModel
from src.ingestion.scrapers.utils import _strip_and_replace
from src.repositories.base_repository import FK
from src.repositories.existencia_stock_repository import ExistenciaStockRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import (
    RepuestoRepository,
    RepuestoUnidadesRepository,
)

logger = logging.getLogger(__name__)


def filtrar_series_regex(df: pd.DataFrame, tipos: dict[str, list[str]]) -> pd.Series:
    palabra_a_tipo = {
        p.lower(): tipo for tipo, palabras in tipos.items() for p in palabras
    }

    alternativas = sorted(palabra_a_tipo, key=len, reverse=True)
    patron = (
        r"\b("
        + "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in alternativas)
        + r")"
    )

    encontrada = (
        df["Descripcion"]
        .str.extract(patron, flags=re.IGNORECASE, expand=False)
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    return encontrada.map(palabra_a_tipo)


def transformar_existencia(
    df: pd.DataFrame, cabecera: CabecerasEnum
) -> list[pd.DataFrame]:
    df = _strip_and_replace(df)
    df = df[DF_EXISTENCIA]
    df = df.rename(columns=RENAME_COLS_EXISTENCIA)
    df_rep: pd.DataFrame = df.copy()

    df = df.sort_values(REPUESTOS_SORT_COLS)
    df["FechaExistencia"] = TODAY
    df["Cabecera"] = cabecera  # type: ignore
    df["Unidad"] = df["Unidad"].replace(RENAME_UNIDADES)  # type: ignore

    for col in REPUESTOS_SORT_COLS:
        df[col] = df[col].astype(float).astype("Int64").astype(str)

    return [df, df_rep]


def transformar_ficha(df: pd.DataFrame, cabecera: CabecerasEnum) -> pd.DataFrame:
    df = _strip_and_replace(df)

    df = df.rename(columns=RENAME_COLS_FICHA)
    df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)
    df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)

    df = df[(df.Familia != 0) & (df.TipoMov != "INI")]

    if cabecera == CabecerasEnum.MEGABUS:
        df = df[(df.Deposito == 9)]

    df = df.sort_values(REPUESTOS_SORT_COLS)
    df, df["FechaMov"] = arreglar_fechas(df, "FechaMov")

    df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
    df["Deposito"] = cabecera  # type: ignore

    es_c = df["Usuario"].str.match(r"^C\d+$", na=False)
    es_u = df["Usuario"].str.match(r"^U\d+$", na=False)
    es_cabecera = df["Usuario"].isin(USUARIOS_CABECERA)
    df["TipoUsuario"] = pd.NA

    df.loc[es_c & ~es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.COCHE.value
    df.loc[es_c & es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.CABECERA.value
    df.loc[es_u, "TipoUsuario"] = TipoUsuarioEnum.USUARIO.value

    df["Usuario"] = (
        df["Usuario"].str.replace({"C": "", "U": "", "c": "", "u": ""}).astype("UInt32")
    )
    df = df.rename(columns={"Usuario": "Interno"})

    for col in REPUESTOS_SORT_COLS:
        df[col] = df[col].astype(float).astype("Int64").astype(str)

    return df


def transformar_repuestos(df: pd.DataFrame) -> pd.DataFrame:
    df["Descripcion"] = df["Descripcion"].str.replace(
        CARACTERES_ERRONEOS,
        regex=True,
    )

    # Para los *N°*
    df["Descripcion"] = df["Descripcion"].str.replace(
        r"(?<=\S)(N°)|(N°)(?=\S)", r" \1\2 ", regex=True
    )

    # Para los P/ C/ S/ E/
    df["Descripcion"] = df["Descripcion"].str.replace(
        r"\b([PCSE])/(?=\S)", r"\1/ ", regex=True
    )

    # Para los ROD.ENG.
    df["Descripcion"] = df["Descripcion"].str.replace(
        r"\.(?=[A-ZÑ])|(?<!\d)\.(?=\d)", ". ", regex=True
    )

    REEMPLAZOS = {}
    for correcto, variantes in SINONIMOS.items():
        for v in variantes:
            if v in REEMPLAZOS:
                raise ValueError(f"'{v}' está repetida: {REEMPLAZOS[v]} y {correcto}")
            REEMPLAZOS[v] = correcto

    claves = sorted(REEMPLAZOS, key=len, reverse=True)
    PATRON = re.compile(r"(?<!\S)(" + "|".join(map(re.escape, claves)) + r")(?!\S)")

    df["Descripcion"] = df["Descripcion"].str.replace(
        PATRON, lambda m: REEMPLAZOS[m.group(1)], regex=True
    )

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

    df["Conjunto"] = df["Descripcion"].str.extract(regex, expand=False).map(KW_CONJUNTO)

    df["Condicion"] = filtrar_series_regex(df, CONDICION_REPUESTOS)
    df["Condicion"] = df["Condicion"].fillna("NUEVO")

    df["Descripcion"] = df["Descripcion"].str.replace(CONDICION)
    df["Descripcion"] = df["Descripcion"].str.strip()

    df["TipoDuracion"] = df["Conjunto"].map(REGLAS_TIPO_DURACION)

    df["Critico"] = False
    df.loc[
        df["Descripcion"].str.contains(
            "CRITICO|CRITICA|CRITICOS|CRITICAS", case=False, na=False
        ),
        "Critico",
    ] = True

    return df


def transformar_repuestos_unidades() -> pd.DataFrame:
    df = pd.DataFrame(
        [
            (fam, art, unid, desd, hast)
            for (fam, art), periodos in REGLAS_UNIDADES_POR_COCHE.items()
            for unid, desd, hast in periodos
        ],
        columns=["Familia", "Articulo", "Unidades", "FechaDesde", "FechaHasta"],
    )

    df["FechaDesde"] = pd.to_datetime(df["FechaDesde"]).dt.date
    df["FechaHasta"] = pd.to_datetime(df["FechaHasta"]).dt.date

    return df


class Local:
    def __init__(self, session: Session, path: CabecerasPathEnum):
        self.repo_ficha = FichaStockRepository()
        self.repo_existencia = ExistenciaStockRepository()
        self.repo_repuesto = RepuestoRepository()
        self.repo_repuesto_unidad = RepuestoUnidadesRepository()
        self.session = session

        self.cabecera = path.value[0]
        self.ruta_server = path.value[1]

    def guardar_existencia_stock(self) -> None:
        ruta = self.ruta_server.ARTSTK

        if not ruta.exists():
            logger.warning("falta %s, se omite la cabecera %s", ruta, self.cabecera)
            return

        df = leer(self.ruta_server.ARTSTK)
        df, df_rep = transformar_existencia(df, self.cabecera)
        self.guardar_repuestos(df_rep)

        df = self.repo_existencia.resolver_fk(
            self.session, df, RepuestoModel, REPUESTOS_SORT_COLS
        )

        df = df.drop(columns=["Nombre"])
        self.repo_existencia.load_df(
            self.session, df, ModoCargaEnum.OVERWRITE, cascade=True
        )

    def guardar_ficha_stock(self) -> None:
        self.repo_ficha.delete_by_cabecera(self.session, self.cabecera)
        self.session.commit()

        self.repo_ficha.load_df_chunks(
            fks=(FK(RepuestoModel, REPUESTOS_PK_COLS),),
            transf_df=partial(transformar_ficha, cabecera=self.cabecera),
            rutas=self.ruta_server.obtener_archivos(),
            df_cols=DF_FICHA,
        )

    def guardar_repuestos(self, df: pd.DataFrame) -> None:
        df = df[REPUESTOS_COLS]
        df = df.rename(columns=RENAME_REPUESTOS)
        df = transformar_repuestos(df)

        self.repo_repuesto.load_df(
            self.session, df, ModoCargaEnum.UPSERT, claves=["Familia", "Articulo"]
        )

        self.guardar_repuestos_unidades()

    def guardar_repuestos_unidades(self) -> None:
        df = self.repo_repuesto_unidad.resolver_fk(
            self.session,
            transformar_repuestos_unidades(),
            RepuestoModel,
            REPUESTOS_SORT_COLS,
        )

        self.repo_repuesto_unidad.load_df(self.session, df, ModoCargaEnum.OVERWRITE)
