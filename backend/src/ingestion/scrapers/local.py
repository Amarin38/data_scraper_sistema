import logging
import time
from datetime import datetime
from functools import partial

import pandas as pd
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
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
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
    REGEX_USER_T,
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
from src.repositories.existencia_stock_repository import (
    ExistenciaStockRepository,
)
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import (
    RepuestoRepository,
    RepuestoUnidadesRepository,
)

logger = logging.getLogger(__name__)


class TransformarLocal:
    def ficha(self, df: pd.DataFrame, cabecera: CabecerasEnum) -> pd.DataFrame:
        df = _strip_and_replace(df)

        df = df.rename(columns=RENAME_COLS_FICHA)

        if cabecera == CabecerasEnum.MEGABUS:
            df = df[(df.Deposito == 9)]
        elif cabecera == CabecerasEnum.POMPEYA:
            df = df[(df.Deposito == 1)]

        df = df.dropna(subset=REPUESTOS_CLAVES_COLS)
        df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)
        df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)

        df = df[(df.Familia != 0) & (df.TipoMov != "INI")]
        df = df[~((df.Familia == 1) & (df.Articulo == 2))]

        df = df.sort_values(REPUESTOS_CLAVES_COLS)
        df, df["FechaMov"] = arreglar_fechas(df, "FechaMov")

        df.loc[df["TipoMov"] == "Salida", "Cantidad"] *= -1
        df["Deposito"] = cabecera.value

        es_c = df["Usuario"].str.match(REGEX_USER_C, na=False)
        es_u = df["Usuario"].str.match(REGEX_USER_U, na=False)
        es_t = df["Usuario"].str.match(REGEX_USER_T, na=False)
        es_cabecera = df["Usuario"].isin(USUARIOS_CABECERA)
        df["TipoUsuario"] = pd.NA

        df.loc[es_c & ~es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.COCHE.value
        df.loc[es_c & es_cabecera, "TipoUsuario"] = TipoUsuarioEnum.CABECERA.value
        df.loc[es_u | es_t, "TipoUsuario"] = TipoUsuarioEnum.USUARIO.value

        df["Usuario"] = (
            pd.to_numeric(df["Usuario"].str.replace(REPLACE_USERS), errors="coerce")
            .round(0)
            .astype("UInt32")
        )
        df = df.rename(columns={"Usuario": "Interno"})

        for col in REPUESTOS_CLAVES_COLS:
            df[col] = df[col].astype(float).astype("Int64").astype(str)

        return df

    def repuestos(self, df: pd.DataFrame) -> pd.DataFrame:
        df = _strip_and_replace(df)
        df = df[DF_EXISTENCIA]
        df = df.rename(columns=RENAME_COLS_EXISTENCIA)
        df = df[REPUESTOS_COLS]
        df = df.rename(columns=RENAME_REPUESTOS)

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
            df["Descripcion"].str.contains(
                FILTER_DESCRIP_CRITICO, case=False, na=False
            ),
            "Critico",
        ] = True

        df = df.sort_values(REPUESTOS_CLAVES_COLS)

        return df

    @staticmethod
    def repuestos_unidades() -> pd.DataFrame:
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


class GuardarLocal:
    def __init__(self, session: Session, path: CabecerasPathEnum):
        self.transformar = TransformarLocal()
        self.repo_ficha = FichaStockRepository()
        self.repo_repuesto = RepuestoRepository()
        self.repo_repuesto_unidad = RepuestoUnidadesRepository()
        self.session = session

        self.cabecera = path.value[0]
        self.ruta_server = path.value[1]

    def ficha_stock(self, tipo: str) -> None:
        if tipo.lower() == "todos":
            rutas = self.ruta_server.obtener_todos()
            self.repo_ficha.delete_by_cabecera(self.session, self.cabecera)
        else:
            rutas = self.ruta_server.obtener_ficart()
            self.repo_ficha.delete_by_cabecera(
                self.session, self.cabecera, parcial=True
            )

        print(f"\n▶ {self.cabecera.name.replace('_', ' ')}")

        if not any(r.exists() for r in rutas):
            for r in rutas:
                print(f"  ⚠ {r.name:<13} no encontrado")
            return

        self.session.commit()

        self.repo_ficha.load_df_chunks(
            fks=(FK(RepuestoModel, REPUESTOS_PK_COLS),),
            transf_df=partial(self.transformar.ficha, cabecera=self.cabecera),
            rutas=rutas,
            df_cols=DF_FICHA,
            etiqueta=self.cabecera.name.lower(),
        )

    def repuestos(self) -> bool:
        """Catálogo desde ARTSTK. False si la cabecera no tiene el archivo."""
        ruta = self.ruta_server.ARTSTK
        if not ruta.exists():
            return False

        t0 = time.perf_counter()
        modif = datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"⟳ {ruta.name}  {modif}")

        df = self.transformar.repuestos(leer(ruta))
        n = self.repo_repuesto.load_df(
            self.session, df, ModoCargaEnum.UPSERT, claves=REPUESTOS_CLAVES_COLS
        )
        n_unid = self.repuestos_unidades()

        print(
            f"✔ {n:,} repuestos · {n_unid} unidades · {time.perf_counter() - t0:.0f}s".replace(
                ",", "."
            )
        )
        return True

    def repuestos_unidades(self) -> int:
        df = self.repo_repuesto_unidad.resolver_fk(
            self.session,
            self.transformar.repuestos_unidades(),
            RepuestoModel,
            REPUESTOS_CLAVES_COLS,
        )
        return self.repo_repuesto_unidad.load_df(
            self.session, df, ModoCargaEnum.OVERWRITE
        )
