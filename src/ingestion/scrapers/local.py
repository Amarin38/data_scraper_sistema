import logging
from functools import partial

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.constants import (
    DF_EXISTENCIA,
    DF_FICHA,
    REGLAS_TIPO_DURACION,
    REGLAS_UNIDADES_POR_COCHE,
    RENAME_COLS_EXISTENCIA,
    RENAME_COLS_FICHA,
    RENAME_MOV,
    RENAME_REPUESTOS,
    RENAME_UNIDADES,
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
from src.core.utils import arreglar_fechas, leer
from src.db.models.repuesto_model import RepuestoModel
from src.ingestion.scrapers.constants import (
    CONDICION_REPUESTOS,
    FILTER_DESCRIP_CRITICO,
    REEMPLAZOS_DESCRIP,
    REGEX_USER_C,
    REGEX_USER_U,
    REPLACE_USERS,
    REPUESTOS_CLAVES_COLS,
    REPUESTOS_COLS,
    REPUESTOS_PK_COLS,
    REPUESTOS_UNIDADES_COLS,
    regex_conjuntos,
    regex_filtrar_series,
)
from src.ingestion.scrapers.utils import _strip_and_replace
from src.repositories.base_repository import FK
from src.repositories.existencia_stock_repository import ExistenciaStockRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import (
    RepuestoRepository,
    RepuestoUnidadesRepository,
)

logger = logging.getLogger(__name__)


def transformar_existencia(df: pd.DataFrame, cabecera: CabecerasEnum):
    df = _strip_and_replace(df)
    df = df[DF_EXISTENCIA]
    df = df.rename(columns=RENAME_COLS_EXISTENCIA)
    df_rep: pd.DataFrame = df.copy()

    df = df.sort_values(REPUESTOS_CLAVES_COLS)
    df["FechaExistencia"] = TODAY
    df["Cabecera"] = cabecera  # type: ignore
    df["Unidad"] = df["Unidad"].replace(RENAME_UNIDADES)  # type: ignore

    for col in REPUESTOS_CLAVES_COLS:
        df[col] = df[col].astype(float).astype("Int64").astype(str)

    return {"df_existencia": df, "df_repuesto": df_rep}


def transformar_ficha(df: pd.DataFrame, cabecera: CabecerasEnum) -> pd.DataFrame:
    df = _strip_and_replace(df)

    df = df.rename(columns=RENAME_COLS_FICHA)
    df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)
    df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)

    df = df[(df.Familia != 0) & (df.TipoMov != "INI")]

    if cabecera == CabecerasEnum.MEGABUS:
        df = df[(df.Deposito == 9)]

    df = df.sort_values(REPUESTOS_CLAVES_COLS)
    df, df["FechaMov"] = arreglar_fechas(df, "FechaMov")

    df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
    df["Deposito"] = cabecera  # type: ignore

    es_c = df["Usuario"].str.match(REGEX_USER_C, na=False)
    es_u = df["Usuario"].str.match(REGEX_USER_U, na=False)
    es_cabecera = df["Usuario"].isin(USUARIOS_CABECERA)
    df["TipoUsuario"] = pd.NA

    df.loc[es_c & ~es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.COCHE.value
    df.loc[es_c & es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.CABECERA.value
    df.loc[es_u, "TipoUsuario"] = TipoUsuarioEnum.USUARIO.value

    df["Usuario"] = df["Usuario"].str.replace(REPLACE_USERS).astype("UInt32")
    df = df.rename(columns={"Usuario": "Interno"})

    for col in REPUESTOS_CLAVES_COLS:
        df[col] = df[col].astype(float).astype("Int64").astype(str)

    return df


def transformar_repuestos(df: pd.DataFrame) -> pd.DataFrame:
    regex_conj = regex_conjuntos()

    df["Condicion"] = regex_filtrar_series(df, CONDICION_REPUESTOS)
    df["Condicion"] = df["Condicion"].fillna("NUEVO")

    for pattrn, repl in REEMPLAZOS_DESCRIP.items():
        df["Descripcion"] = (
            df["Descripcion"].str.strip().str.replace(pattrn, repl, regex=True)
        )

    df["Conjunto"] = (
        df["Descripcion"]
        .str.extract(regex_conj["regex"], expand=False)
        .map(regex_conj["kw"])
    )

    df["TipoDuracion"] = df["Conjunto"].map(REGLAS_TIPO_DURACION)

    df["Critico"] = False
    df.loc[
        df["Descripcion"].str.contains(FILTER_DESCRIP_CRITICO, case=False, na=False),
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
        columns=REPUESTOS_UNIDADES_COLS,
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
        dfs = transformar_existencia(df, self.cabecera)
        self.guardar_repuestos(dfs["df_repuesto"])

        dfs["df_existencia"] = self.repo_existencia.resolver_fk(
            self.session, dfs["df_existencia"], RepuestoModel, REPUESTOS_CLAVES_COLS
        )

        dfs["df_existencia"] = dfs["df_existencia"].drop(columns=["Nombre"])
        self.repo_existencia.load_df(
            self.session, dfs["df_existencia"], ModoCargaEnum.OVERWRITE
        )

    def guardar_ficha_stock(self) -> None:
        rutas = self.ruta_server.obtener_archivos()

        if not rutas:
            return

        self.repo_ficha.delete_by_cabecera(self.session, self.cabecera)
        self.session.commit()

        self.repo_ficha.load_df_chunks(
            fks=(FK(RepuestoModel, REPUESTOS_PK_COLS),),
            transf_df=partial(transformar_ficha, cabecera=self.cabecera),
            rutas=rutas,
            df_cols=DF_FICHA,
        )

    def guardar_repuestos(self, df: pd.DataFrame) -> None:
        df = df[REPUESTOS_COLS]
        df = df.rename(columns=RENAME_REPUESTOS)
        df = transformar_repuestos(df)

        self.repo_repuesto.load_df(
            self.session, df, ModoCargaEnum.UPSERT, claves=REPUESTOS_CLAVES_COLS
        )

        self.guardar_repuestos_unidades()

    def guardar_repuestos_unidades(self) -> None:
        df = self.repo_repuesto_unidad.resolver_fk(
            self.session,
            transformar_repuestos_unidades(),
            RepuestoModel,
            REPUESTOS_CLAVES_COLS,
        )

        self.repo_repuesto_unidad.load_df(self.session, df, ModoCargaEnum.OVERWRITE)
