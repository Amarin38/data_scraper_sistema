import logging
import time
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import repeat
from typing import Generic, TypeVar

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.orm import Session

from core.enums import ModoCargaEnum
from src.db import dbbase
from src.db.session import SessionLocal
from src.ingestion.scrapers.utils import _chunks_de

logger = logging.getLogger(__name__)
TModel = TypeVar("TModel", bound=dbbase)

_repos: dict[type, BaseRepository] = {}
_refs: dict[FK, pd.DataFrame] = {}


@dataclass(frozen=True)
class FK:
    model: type
    claves: tuple[str, ...]


@dataclass(frozen=True)
class TareaCarga:
    """Se le tiene que pasar un Repository, un partial
    y un FK con el model y las claves"""

    repo_cls: type[BaseRepository]
    transformar: Callable[[pd.DataFrame], pd.DataFrame]
    fks: tuple[FK, ...] = ()


class CargaParalela:
    def _repo(self, cls: type[BaseRepository]) -> BaseRepository:
        if cls not in _repos:
            _repos[cls] = cls()
        return _repos[cls]

    def procesar_chunk(self, df: pd.DataFrame, tarea: TareaCarga) -> int:
        repo = self._repo(tarea.repo_cls)

        # al salir del with la sesión se cierra; si no hubo commit, hace rollback
        with SessionLocal() as session:
            df = tarea.transformar(df)

            for fk in tarea.fks:
                if fk not in _refs:  # la tabla de referencia se lee una vez por worker
                    _refs[fk] = repo.leer_ref(session, fk.model, list(fk.claves))
                df = repo.resolver_fk(
                    session, df, fk.model, list(fk.claves), df_ref=_refs[fk]
                )

            n = repo.load_df_copy(session, df)
            session.commit()
        return n

    def cargar_en_paralelo(
        self, chunks: Iterable[pd.DataFrame], tarea: TareaCarga, n_workers: int = 2
    ) -> int:
        # en modo secuencial el cache vive en este proceso: se limpia para no
        # usar IDs de una corrida anterior
        _refs.clear()

        if n_workers <= 1:
            return sum(self.procesar_chunk(df, tarea) for df in chunks)

        total = 0
        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            # buffersize: solo unos pocos chunks en vuelo, no serializa todo de una
            for n in ex.map(
                self.procesar_chunk, chunks, repeat(tarea), buffersize=n_workers * 2
            ):
                total += n
        return total


class BaseRepository(Generic[TModel]):  # noqa: UP046
    model: type[TModel]

    def __init__(self):
        self.table_name = self.model.__tablename__
        self.tabla = self.model.__table__
        self.pk = inspect(self.model).primary_key[0]

    # ------------------------------------------------------------------ CRUD

    def get_by_id(self, db: Session, id_: int) -> TModel | None:
        return db.get(self.model, id_)

    def listar(
        self, db: Session, *, limit: int = 100, cursor: int | None = None
    ) -> Sequence[TModel]:
        stmt = select(self.model).order_by(self.pk).limit(limit)
        if cursor is not None:
            stmt = stmt.where(self.pk > cursor)
        return db.scalars(stmt).all()

    def listar_pagina(self, db, limit, cursor) -> tuple[Sequence[TModel], int | None]:
        """Lista en formato paginado, devolviendo los items
        de la página y el siguiente cursor."""

        items = self.listar(db, limit=limit, cursor=cursor)
        next_cursor = getattr(items[-1], self.pk.name) if len(items) == limit else None
        return items, next_cursor

    def add(self, db: Session, obj: TModel) -> TModel:
        db.add(obj)
        db.flush()
        return obj

    def delete_by_obj(self, db: Session, obj: TModel) -> None:
        """Borra una fila ya cargada en la sesión.
        - Respeta cascades y eventos ORM.
        - No conviene para borrado masivo.
        - Más lento que el borrado crudo.
        """
        db.delete(obj)

    def delete_where(self, db: Session, *condiciones) -> int:
        """DELETE directo, sin traer filas.
        - No dispara cascades ni eventos ORM.
        - Para borrados masivos.
        - Más rápido que el borrado por objeto.
        - Devuelve filas afectadas.
        """
        stmt = delete(self.model).where(*condiciones)
        return db.execute(stmt).rowcount  # type: ignore

    # --------------------------------------------------------- carga masiva

    def load_df_copy(
        self, db: Session, df: pd.DataFrame, tabla: str | None = None
    ) -> int:
        """COPY FROM STDIN dentro de la transacción de la sesión. No commitea."""
        self._validar(df)
        df = df.copy()

        dialect = db.get_bind().dialect
        for col in df.columns:
            proc = self.tabla.c[col].type.bind_processor(dialect)
            if proc is not None:
                df[col] = df[col].map(lambda v, p=proc: None if pd.isna(v) else p(v))

        enteros = {
            i
            for i, c in enumerate(df.columns)
            if "INT" in str(self.tabla.c[c].type).upper()
        }

        destino = tabla or self.table_name
        cols = ", ".join(f'"{c}"' for c in df.columns)
        dbapi_conn = db.connection().connection

        with (
            dbapi_conn.cursor() as cur,  # type: ignore
            cur.copy(f'COPY "{destino}" ({cols}) FROM STDIN') as copy,
        ):
            for row in df.itertuples(index=False, name=None):
                fila = []
                for i, v in enumerate(row):
                    if pd.isna(v):
                        fila.append(None)
                    elif i in enteros:
                        fila.append(int(v))
                    else:
                        fila.append(v)
                copy.write_row(fila)
        return len(df)

    def load_df(
        self,
        db: Session,
        df: pd.DataFrame,
        modo: ModoCargaEnum = ModoCargaEnum.APPEND,
        claves: list[str] | None = None,
        cascade: bool = False,
        commit: bool = True,
    ) -> int:
        """Carga un df según el modo:

        append    -> agrega filas (historial, ficha_stock).
        overwrite -> TRUNCATE + carga. Solo para tablas sin hijos, o con cascade=True.
        upsert    -> inserta las nuevas y actualiza las existentes por `claves`.
                     Preserva los IDs, así que es lo que va en tablas padre.
        """
        t0 = time.perf_counter()
        try:
            match modo:
                case ModoCargaEnum.OVERWRITE:
                    sufijo = " CASCADE" if cascade else ""
                    db.execute(text(f'TRUNCATE TABLE "{self.table_name}"{sufijo}'))
                    n = self.load_df_copy(db, df)

                case ModoCargaEnum.APPEND:
                    n = self.load_df_copy(db, df)

                case ModoCargaEnum.UPSERT:
                    if not claves:
                        raise ValueError("upsert necesita `claves`")
                    n = self._upsert(db, df, claves)

            if commit:
                db.commit()
            print(
                f"[{self.table_name}] {modo}: {n} filas en {time.perf_counter() - t0:.1f}s"
            )
            return n
        except Exception:
            db.rollback()
            raise

    def load_df_chunks(
        self,
        fks: tuple[FK, ...],
        transf_df: Callable,
        rutas: list[str] | str,
        df_cols: list[str],
        n_workers: int = 2,
        chunk_size: int = 200_000,
    ):
        t0 = time.perf_counter()

        tarea = TareaCarga(
            repo_cls=type(self),
            transformar=transf_df,
            fks=fks,
        )

        chunks = _chunks_de(rutas, chunk_size, df_cols)
        insertadas = CargaParalela().cargar_en_paralelo(chunks, tarea, n_workers)
        print(f"[{self.table_name}]: +{insertadas} en {time.perf_counter() - t0:.1f}s")

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
            raise ValueError(
                f"faltan: {esperadas - actuales} | sobran: {actuales - esperadas}"
            )

        obligatorias = [
            c.name for c in self.tabla.columns if not c.nullable and not c.primary_key
        ]
        nulos = df[obligatorias].isna().sum()
        if nulos.any():
            raise ValueError(f"nulos en obligatorias:\n{nulos[nulos > 0]}")

    def _normalizar_merge(self, s1: pd.Series, s2: pd.Series):
        if s1.dtype == object:
            s1 = s1.map(lambda v: v.value if hasattr(v, "value") else v)
        if s2.dtype == object:
            s2 = s2.map(lambda v: v.value if hasattr(v, "value") else v)
        if is_numeric_dtype(s1) and is_numeric_dtype(s2):
            return s1.astype("Int64"), s2.astype("Int64")
        return s1.astype("string"), s2.astype("string")

    def _upsert(self, db: Session, df: pd.DataFrame, claves: list[str]) -> int:
        cols = [f'"{c}"' for c in df.columns]
        lista = ", ".join(cols)
        stg = f"stg_{self.table_name}"

        # staging sin constraints ni defaults: solo los tipos de las columnas del df
        db.execute(
            text(
                f'CREATE TEMP TABLE "{stg}" ON COMMIT DROP AS '
                f'SELECT {lista} FROM "{self.table_name}" WITH NO DATA'
            )
        )
        self.load_df_copy(db, df, tabla=stg)

        k = ", ".join(f'"{c}"' for c in claves)
        updates = [f'"{c}" = EXCLUDED."{c}"' for c in df.columns if c not in claves]
        accion = f"DO UPDATE SET {', '.join(updates)}" if updates else "DO NOTHING"

        res = db.execute(
            text(
                f'INSERT INTO "{self.table_name}" ({lista}) '
                f'SELECT DISTINCT ON ({k}) {lista} FROM "{stg}" ORDER BY {k} '
                f"ON CONFLICT ({k}) {accion}"
            )
        )
        return res.rowcount  # type: ignore
