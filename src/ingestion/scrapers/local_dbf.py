import numpy as np
import pandas as pd
from dbfread import DBF
from sqlalchemy.orm import Session

from core.enums import CabecerasEnum
from src.core.constants import (
    DF_EXISTENCIA,
    DF_FICHA,
    RENAME_COLS_EXISTENCIA,
    RENAME_COLS_FICHA,
    RENAME_MOV,
    RENAME_UNIDADES,
    RUTA_SERVER_ARTSTK,
    RUTA_SERVER_FICANT,
    RUTA_SERVER_FICANT1,
    RUTA_SERVER_FICART,
    SORT_COLS,
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
    TODAY_EXISTENCIA,
)
from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.existencia_stock_repository import ExistenciaStockRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import RepuestoRepository


class LocalDBF:
    def __init__(self, session: Session, cabecera: CabecerasEnum):
        self.repo_ficha = FichaStockRepository()
        self.repo_existencia = ExistenciaStockRepository()
        self.repo_repuesto = RepuestoRepository()
        self.session = session
        self.cabecera = cabecera

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

    # --------- OBTENER ---------

    def obtener_existencia_stock(self) -> pd.DataFrame:
        df = self.leer(RUTA_SERVER_ARTSTK)

        df = df[DF_EXISTENCIA]
        df = df.rename(columns=RENAME_COLS_EXISTENCIA)  # type: ignore
        df = df.sort_values(SORT_COLS)
        df["FechaExistencia"] = TODAY_EXISTENCIA
        df["Cabecera"] = self.cabecera
        df["Unidad"] = df["Unidad"].replace(RENAME_UNIDADES)

        df["Stock"] = self.limpiar_vacio(df["Stock"])
        df["Unidad"] = self.limpiar_vacio(df["Unidad"])

        for col in ["Familia", "Articulo"]:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        print(df)
        return df

    def obtener_ficha_stock(self) -> pd.DataFrame:
        rutas = [RUTA_SERVER_FICANT, RUTA_SERVER_FICANT1, RUTA_SERVER_FICART]
        dfs_finales = []

        for r in rutas:
            print(r)
            dfs_finales.append(self.leer(r))

        df = pd.concat(dfs_finales, ignore_index=False)

        df = df[DF_FICHA]
        df = df.rename(columns=RENAME_COLS_FICHA)  # type: ignore
        df = df.sort_values(SORT_COLS)
        df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)

        df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)
        df["FechaMov"] = pd.to_datetime(df["FechaMov"], errors="coerce")

        df = df[(df.Familia != 0) & (df.Deposito == 9) & (df.TipoMov != "INI")]

        df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
        df["Deposito"] = self.cabecera

        df["DepositoTransfer"] = self.limpiar_vacio(df["DepositoTransfer"])
        df["Usuario"] = self.limpiar_vacio(df["Usuario"])
        df["PrecioUnitario"] = self.limpiar_vacio(df["PrecioUnitario"])

        for col in ["Familia", "Articulo"]:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        return df  # type: ignore

    def obtener_repuestos(self) -> pd.DataFrame:
        df = self.obtener_existencia_stock()
        df = df[["Familia", "Articulo", "Nombre"]]
        df = df.rename(columns={"Nombre": "Descripcion"})  # type: ignore

        return df

    # --------- GUARDAR ---------

    def guardar_existencia_stock(self) -> None:
        df = self.obtener_existencia_stock()

        df = self.repo_existencia.resolver_fk(
            self.session, df,  RepuestoModel, ["Familia", "Articulo"]
        )

        self.repo_existencia.load_df_with_overwrite(df, self.session)

        self.session.commit()

    def guardar_ficha_stock(self) -> None:
        df = self.obtener_ficha_stock()

        df = self.repo_existencia.resolver_fk(
            self.session, df, RepuestoModel, ["Familia", "Articulo"]
        )
        self.repo_ficha.load_df_with_overwrite(df, self.session)
        self.session.commit()

    def guardar_repuestos(self) -> None:
        self.repo_repuesto.load_df_with_overwrite(
            self.obtener_repuestos(), self.session
        )
        self.session.commit()

    # --------- UTILIDADES ---------

    def limpiar_tabla(self):
        self.repo_ficha.limpiar_tabla(self.session)

    def calcular_tamaño(self):
        self.repo_ficha.calcular_tamaño(self.session)

    def limpiar_vacio(self, col) -> pd.DataFrame:
        return (
            col.replace(0, np.nan)
            .replace("0", np.nan)
            .replace("", np.nan)
            .replace(0.0, np.nan)
        )
