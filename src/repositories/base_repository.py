import logging
import time
from collections.abc import Sequence
from typing import Generic, TypeVar

from core.constants import BASURA
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sqlalchemy import Integer, inspect, select, text
from sqlalchemy.orm import Session

from src.db import dbbase

logger = logging.getLogger(__name__)

TModel = TypeVar("TModel", bound=dbbase)  # type: ignore


class BaseRepository(Generic[TModel]):  # noqa: UP046
    model: type[TModel]

    def __init__(self):
        self.table_name = self.model.__tablename__
        self.tabla = self.model.__table__
        self.pk = inspect(self.model).primary_key[0]

    # ------------------------------------------------------------------ CRUD

    def get_by_id(self, db: Session, id_: int) -> TModel | None:
        return db.get(self.model, id_)

    def list(self, db: Session, *, limit: int = 100, cursor: int | None = None) -> Sequence[TModel]:
        stmt = select(self.model).order_by(self.pk).limit(limit)
        if cursor is not None:
            stmt = stmt.where(self.pk > cursor)
        return db.scalars(stmt).all()

    def add(self, db: Session, obj: TModel) -> TModel:
        db.add(obj)
        db.flush()
        return obj

    def delete_by_obj(self, db: Session, obj: TModel) -> None:
        db.delete(obj)
        db.flush()

    def delete_by_id(self, db: Session, id_: int) -> bool:
        obj = self.get_by_id(db, id_)
        if obj is None:
            return False
        self.delete_by_obj(db, obj)
        return True

    # --------------------------------------------------------- carga masiva

    def load_df(self, db: Session, df: pd.DataFrame, chunk: int = 50000, commit: bool = True) -> int:
        """Insert con executemany. Más lento que load_df_copy; queda por compatibilidad."""
        self._validar(df)
        df = df.astype(object).where(pd.notna(df), None)
        registros = df.to_dict("records")

        total = (len(registros) + chunk - 1) // chunk
        insertadas = 0

        for n, i in enumerate(range(0, len(registros), chunk)):
            tc = time.perf_counter()
            res = db.execute(self.tabla.insert(), registros[i : i + chunk])  # type: ignore
            insertadas += res.rowcount
            if commit and n % 10 == 9:
                db.commit()
            print(f"  chunk {n + 1}/{total}: {time.perf_counter() - tc:.1f}s")

        if commit:
            db.commit()
        return insertadas


    def load_df_copy(self, db: Session, df: pd.DataFrame) -> int:
        """COPY FROM STDIN dentro de la transacción de la sesión. No commitea."""
        self._validar(df)

        dialect = db.get_bind().dialect
        for col in df.columns:
            proc = self.tabla.c[col].type.bind_processor(dialect)
            if proc is not None:
                df[col] = df[col].map(lambda v, p=proc: None if pd.isna(v) else p(v))

        cols = ", ".join(f'"{c}"' for c in df.columns)
        dbapi_conn = db.connection().connection

        # índices de las columnas que en la base son enteras
        enteros = {
            i for i, c in enumerate(df.columns)
            if "INT" in str(self.tabla.c[c].type).upper()
        }

        with (
            dbapi_conn.cursor() as cur,
            cur.copy(f'COPY "{self.table_name}" ({cols}) FROM STDIN') as copy,
        ):
            for row in df.itertuples(index=False, name=None):
                fila = []
                for i, v in enumerate(row):
                    if v is None or pd.isna(v):
                        fila.append(None)
                    elif i in enteros:
                        fila.append(int(v))
                    else:
                        fila.append(v)
                copy.write_row(fila)
        return len(df)
    

    def load_df_with_overwrite(self, db: Session, df: pd.DataFrame) -> int:
        t0 = time.perf_counter()
        try:
            db.execute(text(f'TRUNCATE TABLE "{self.table_name}" CASCADE'))
            insertadas = self.load_df_copy(db, df)
            db.commit()
            print(f"[{self.table_name}] {insertadas} filas en {time.perf_counter() - t0:.1f}s")
            return insertadas
        except Exception:
            db.rollback()
            raise

    # ------------------------------------------------------------------ FKs

    def leer_ref(self, db: Session, model, claves: list[str]) -> pd.DataFrame:
        pk = self._pk_simple(model)
        cols = [model.__table__.c[c] for c in [pk, *claves]]
        return pd.read_sql(select(*cols), db.bind)  # type: ignore

    def resolver_fk(
        self,
        db: Session,
        df_main: pd.DataFrame,
        model_to_merge,
        claves_to_merge: list[str],
        descartar: bool = True,
        df_ref: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        pk = self._pk_simple(model_to_merge)

        if df_ref is None:
            df_ref = self.leer_ref(db, model_to_merge, claves_to_merge)
        else:
            df_ref = df_ref.copy()  # no modificar el cache del llamador

        for c in claves_to_merge:
            df_main[c], df_ref[c] = self._normalizar_merge(df_main[c], df_ref[c])

        df = df_main.merge(df_ref, on=claves_to_merge, how="left")

        faltantes = df[pk].isna().sum()
        if faltantes:
            logger.warning(
                "%d filas sin %s para %s",
                faltantes,
                model_to_merge.__tablename__,
                claves_to_merge,
            )
            if descartar:
                df = df.dropna(subset=[pk])

        df[pk] = df[pk].astype("Int64")
        return df.drop(columns=claves_to_merge)

    # -------------------------------------------------------------- helpers

    def _pk_simple(self, model) -> str:
        pks = inspect(model).primary_key
        if len(pks) != 1:
            raise ValueError(f"{model.__tablename__} no tiene PK simple")
        return pks[0].name

    def _validar(self, df: pd.DataFrame) -> None:
        esperadas = {c.name for c in self.tabla.columns if not c.primary_key}
        actuales = set(df.columns)
        if esperadas != actuales:
            raise ValueError(f"faltan: {esperadas - actuales} | sobran: {actuales - esperadas}")

        obligatorias = [c.name for c in self.tabla.columns if not c.nullable and not c.primary_key]
        nulos = df[obligatorias].isna().sum()
        if nulos.any():
            raise ValueError(f"nulos en obligatorias:\n{nulos[nulos > 0]}")

    def _normalizar_merge(self, s1: pd.Series, s2: pd.Series):
        if s1.dtype == object:
            s1 = s1.map(lambda v: v.value if hasattr(v, "value") else v)  # type: ignore
        if s2.dtype == object:
            s2 = s2.map(lambda v: v.value if hasattr(v, "value") else v)  # type: ignore
        if is_numeric_dtype(s1) and is_numeric_dtype(s2):
            return s1.astype("Int64"), s2.astype("Int64")
        return s1.astype("string"), s2.astype("string")