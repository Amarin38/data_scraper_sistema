import time
from typing import Generic, List, TypeVar
from venv import logger

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sqlalchemy import insert, inspect, select, text
from sqlalchemy.orm import Session

from src.db import dbbase

TModel = TypeVar("TModel", bound=dbbase)  # type: ignore


class BaseRepository(Generic[TModel]):
    model: type[TModel]

    def __init__(self):
        self.table_name = self.model.__tablename__
        self.tabla = self.model.__table__

    def get(self, db: Session, id_: int) -> TModel | None:
        return db.get(self.model, id_)

    def list(self, db: Session, *, limit: int = 50, offset: int = 0) -> list[TModel]:  # type: ignore
        stmt = select(self.model).limit(limit).offset(offset)

        return list(db.scalars(stmt))

    def add(self, db: Session, obj: TModel) -> TModel:
        db.add(obj)
        db.flush()
        return obj

    def _validar(self, df: pd.DataFrame) -> None:
        esperadas = {c.name for c in self.tabla.columns if not c.primary_key}
        actuales = set(df.columns)
        if esperadas != actuales:
            raise ValueError(f"faltan: {esperadas - actuales} | sobran: {actuales - esperadas}")
    
        obligatorias = [
            c.name for c in self.tabla.columns if not c.nullable and not c.primary_key
        ]
        nulos = df[obligatorias].isna().sum()
        if nulos.any():
            raise ValueError(f"nulos en obligatorias:\n{nulos[nulos > 0]}")
    
    
    def load_df(self, df: pd.DataFrame, db: Session, chunk: int = 50000) -> int:
        self._validar(df)
        df = df.astype(object).where(pd.notna(df), None)
        registros = df.to_dict("records")
    
        total = (len(registros) + chunk - 1) // chunk
        insertadas = 0
    
        for n, i in enumerate(range(0, len(registros), chunk)):
            tc = time.perf_counter()
            res = db.execute(self.tabla.insert(), registros[i : i + chunk])
            insertadas += res.rowcount
            if n % 10 == 9:
                db.commit()
            print(f"  chunk {n + 1}/{total}: {time.perf_counter() - tc:.1f}s")
    
        db.commit()
        return insertadas
    
    
    def load_df_with_overwrite(self, df: pd.DataFrame, db: Session, chunk: int = 50000) -> int:
        t0 = time.perf_counter()
        try:
            db.execute(text("SET session_replication_role = 'replica'"))
            db.execute(text(f'TRUNCATE TABLE "{self.table_name}" CASCADE'))
            insertadas = self.load_df(df, db, chunk)
            print(f"[{self.table_name}] {insertadas} filas en {time.perf_counter() - t0:.1f}s")
            return insertadas
        except Exception:
            db.rollback()
            raise
        finally:
            db.execute(text("SET session_replication_role = 'origin'"))
            db.commit()

    def limpiar_tabla(self, db: Session) -> None:
        table_name = self.table_name

        db.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
        db.execute(
            text("""
            SELECT schemaname, relname,
                   ROUND(pg_total_relation_size(relid)/1024.0/1024.0, 1) AS mb
            FROM pg_catalog.pg_statio_user_tables
            ORDER BY pg_total_relation_size(relid) DESC;
            """)
        )
        db.commit()
        print(db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar())

    def resolver_fk(
        self,
        db: Session,
        df_main: pd.DataFrame,
        model_to_merge,
        claves_to_merge: List[str],
        descartar: bool = True,
    ) -> pd.DataFrame:
        pks = inspect(model_to_merge).primary_key
        if len(pks) != 1:
            raise ValueError(f"{model_to_merge.__tablename__} no tiene PK simple")
        pk = pks[0].name

        cols = [model_to_merge.__table__.c[c] for c in [pk, *claves_to_merge]]
        df_ref = pd.read_sql(select(*cols), db.bind)

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

    def _normalizar_merge(self, s1: pd.Series, s2: pd.Series):
        if s1.dtype == object:
            s1 = s1.map(lambda v: v.value if hasattr(v, "value") else v)
        if s2.dtype == object:
            s2 = s2.map(lambda v: v.value if hasattr(v, "value") else v)
        if is_numeric_dtype(s1) and is_numeric_dtype(s2):
            return s1.astype("Int64"), s2.astype("Int64")
        return s1.astype(str), s2.astype(str)
