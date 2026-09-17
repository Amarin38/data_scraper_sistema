import time
from functools import partial

import pandas as pd
from sqlalchemy.orm import Session

from core.enums import ModoCargaEnum
from src.core.constants import (
    DF_EXISTENCIA,
    DF_FICHA,
    RENAME_COLS_EXISTENCIA,
    RENAME_COLS_FICHA,
    RENAME_MOV,
    RENAME_REPUESTOS,
    RENAME_UNIDADES,
    REPUESTOS_COLS,
    SORT_COLS,
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
    TODAY,
)
from src.core.enums import CabecerasEnum, CabecerasPathEnum
from src.db.models.repuesto_model import RepuestoModel
from src.ingestion.carga_paralela import FK, TareaCarga, cargar_en_paralelo
from src.ingestion.scrapers.utils import _chunks_de, _strip_and_replace, leer
from src.repositories.existencia_stock_repository import ExistenciaStockRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import RepuestoRepository


class Local:
    def __init__(self, session: Session, path: CabecerasPathEnum):
        self.repo_ficha = FichaStockRepository()
        self.repo_existencia = ExistenciaStockRepository()
        self.repo_repuesto = RepuestoRepository()
        self.session = session

        self.cabecera = path.value[0]
        self.ruta_server = path.value[1]

    def transformar_existencia(
        self, df: pd.DataFrame, cabecera: CabecerasEnum
    ) -> pd.DataFrame:
        df = _strip_and_replace(df)
        df = df[DF_EXISTENCIA]
        df = df.rename(columns=RENAME_COLS_EXISTENCIA)
        self.guardar_repuestos(df)

        df = df.sort_values(SORT_COLS)
        df["FechaExistencia"] = TODAY
        df["Cabecera"] = cabecera  # type: ignore
        df["Unidad"] = df["Unidad"].replace(RENAME_UNIDADES)  # type: ignore

        for col in SORT_COLS:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        return df

    def transformar_ficha(
        self, df: pd.DataFrame, cabecera: CabecerasEnum
    ) -> pd.DataFrame:
        df = _strip_and_replace(df)

        df = df.rename(columns=RENAME_COLS_FICHA)
        df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)
        df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)

        df = df[(df.Familia != 0) & (df.TipoMov != "INI")]

        if cabecera == CabecerasEnum.MEGABUS:
            df = df[(df.Deposito == 9)]

        df = df.sort_values(SORT_COLS)

        df["FechaMov"] = pd.to_datetime(df["FechaMov"], errors="coerce")
        df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
        df["Deposito"] = cabecera  # type: ignore

        for col in SORT_COLS:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        return df

    def guardar_existencia_stock(self) -> None:
        df = leer(self.ruta_server.ARTSTK)
        df = self.transformar_existencia(df, self.cabecera)
        df = self.repo_existencia.resolver_fk(
            self.session, df, RepuestoModel, list(SORT_COLS)
        )

        self.repo_existencia.load_df(
            self.session, df, ModoCargaEnum.OVERWRITE, cascade=True
        )

    def guardar_ficha_stock(self) -> None:
        self.repo_ficha.delete_by_cabecera(self.session, self.cabecera)
        self.session.commit()
        self.repo_ficha.load_df_chunks(
            fks=(FK(RepuestoModel, SORT_COLS),),
            transf_df=partial(self.transformar_ficha, cabecera=self.cabecera),
            rutas=self.ruta_server.obtener_archivos(),
            df_cols=DF_FICHA,
        )

    def guardar_repuestos(self, df: pd.DataFrame) -> None:
        df = df[REPUESTOS_COLS]
        df = df.rename(columns=RENAME_REPUESTOS)
        self.repo_repuesto.load_df(
            self.session, df, ModoCargaEnum.UPSERT, claves=["Familia", "Articulo"]
        )
