from itertools import islice
from pathlib import Path
from venv import logger

import pandas as pd
from dbfread import DBF
from sqlalchemy.orm import Session

from src.core.constants import (
    DF_EXISTENCIA,
    DF_FICHA,
    RENAME_COLS_EXISTENCIA,
    RENAME_COLS_FICHA,
    RENAME_MOV,
    RENAME_REPUESTOS,
    RENAME_UNIDADES,
    SORT_COLS,
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
    TODAY,
)
from src.core.enums import CabecerasPathEnum
from src.db.models.repuesto_model import RepuestoModel
from src.ingestion.scrapers.utils import _strip_and_replace
from src.repositories.existencia_stock_repository import ExistenciaStockRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import RepuestoRepository


class LocalDBF:
    def __init__(self, session: Session, path: CabecerasPathEnum):
        self.repo_ficha = FichaStockRepository()
        self.repo_existencia = ExistenciaStockRepository()
        self.repo_repuesto = RepuestoRepository()
        self.session = session

        self.cabecera = path.value[0]
        self.ruta_server = path.value[1]

    def leer(self, p):
        return pd.DataFrame(
            iter(
                DBF(
                    p,
                    encoding="cp850",
                    char_decode_errors="ignore",
                    load=False,
                    ignore_missing_memofile=True,
                )
            )
        )

    def leer_chunks(self, p, size=800_000):
        tabla = DBF(
            p,
            encoding="cp850",
            char_decode_errors="ignore",
            load=False,
            ignore_missing_memofile=True,
        )
        it = iter(tabla)
        while True:
            lote = list(islice(it, size))
            if not lote:
                break
            yield pd.DataFrame(lote)


    def guardar_existencia_stock(self) -> None:
        df = self.leer(self.ruta_server.ARTSTK)
        df = _strip_and_replace(df)
        df = df[DF_EXISTENCIA]
        df = df.rename(columns=RENAME_COLS_EXISTENCIA)
        self.guardar_repuestos(df)

        df = df.sort_values(SORT_COLS)
        df["FechaExistencia"] = TODAY
        df["Cabecera"] = self.cabecera # type: ignore
        df["Unidad"] = df["Unidad"].replace(RENAME_UNIDADES)

        for col in ["Familia", "Articulo"]:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        df = self.repo_existencia.resolver_fk(
            self.session, df, RepuestoModel, ["Familia", "Articulo"]
        )

        self.repo_existencia.load_df_with_overwrite(self.session, df)


    def guardar_ficha_stock(self, chunked: bool = True) -> None:
        rutas = self.ruta_server.obtener_archivos()
        primero = True

        for r in rutas:
            print(r)
            if not Path(r).exists():
                logger.warning("falta %s, se omite", r)
                continue
            if chunked:
                for df in self.leer_chunks(r):
                    df = _strip_and_replace(df)

                    df = df[DF_FICHA]
                    df = df.rename(columns=RENAME_COLS_FICHA)
                    df = df.sort_values(SORT_COLS)
                    df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)

                    df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)
                    df["FechaMov"] = pd.to_datetime(df["FechaMov"], errors="coerce")

                    df = df[(df.Familia != 0) & (df.Deposito == 9) & (df.TipoMov != "INI")]

                    df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
                    df["Deposito"] = self.cabecera # type: ignore

                    for col in ["Familia", "Articulo"]:
                        df[col] = df[col].astype(float).astype("Int64").astype(str)

                    df = self.repo_existencia.resolver_fk(
                        self.session, df, RepuestoModel, ["Familia", "Articulo"]
                    )

                    if primero:
                        self.repo_ficha.load_df_with_overwrite_cabecera(self.session, df, self.cabecera)
                        primero = False
                    else:
                        self.repo_ficha.load_df(self.session, df)


    def guardar_repuestos(self, df) -> None:
        df = df[["Familia", "Articulo", "Nombre"]]
        df = df.rename(columns=RENAME_REPUESTOS)

        self.repo_repuesto.load_df_with_overwrite(self.session, df)
