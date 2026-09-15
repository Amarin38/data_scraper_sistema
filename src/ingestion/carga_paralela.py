"""Carga paralela genérica.

El proceso principal lee y reparte chunks crudos. Cada worker, con su propia
sesión, transforma el chunk, resuelve las FKs y lo carga con COPY.

Todo lo que viaja en TareaCarga se serializa (pickle) hacia los workers:
funciones a nivel de módulo, clases y valores simples. Nada de sesiones,
conexiones, lambdas ni métodos de instancia.
"""

from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import repeat

import pandas as pd

from src.db.session import SessionLocal  # ajustá al módulo donde tengas tu sessionmaker
from src.repositories.base_repository import BaseRepository


@dataclass(frozen=True)
class FK:
    model: type
    claves: tuple[str, ...]


@dataclass(frozen=True)
class TareaCarga:
    repo_cls: type[BaseRepository]
    transformar: Callable[[pd.DataFrame], pd.DataFrame]
    fks: tuple[FK, ...] = ()


# Estado por proceso: cada worker tiene su propia copia.
_repos: dict[type, BaseRepository] = {}
_refs: dict[FK, pd.DataFrame] = {}


def _repo(cls: type[BaseRepository]) -> BaseRepository:
    if cls not in _repos:
        _repos[cls] = cls()
    return _repos[cls]


def procesar_chunk(df: pd.DataFrame, tarea: TareaCarga) -> int:
    repo = _repo(tarea.repo_cls)

    # al salir del with la sesión se cierra; si no hubo commit, hace rollback
    with SessionLocal() as session:
        df = tarea.transformar(df)

        for fk in tarea.fks:
            if fk not in _refs:  # la tabla de referencia se lee una vez por worker
                _refs[fk] = repo.leer_ref(session, fk.model, list(fk.claves))
            df = repo.resolver_fk(session, df, fk.model, list(fk.claves), df_ref=_refs[fk])

        n = repo.load_df_copy(session, df)
        session.commit()
    return n


def cargar_en_paralelo(
    chunks: Iterable[pd.DataFrame], tarea: TareaCarga, n_workers: int = 2
) -> int:
    # en modo secuencial el cache vive en este proceso: se limpia para no
    # usar IDs de una corrida anterior
    _refs.clear()

    if n_workers <= 1:  # todo en el proceso principal: sirve para depurar con breakpoints
        return sum(procesar_chunk(df, tarea) for df in chunks)

    total = 0
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        # buffersize: solo unos pocos chunks en vuelo, no serializa todo de una
        for n in ex.map(procesar_chunk, chunks, repeat(tarea), buffersize=n_workers * 2):
            total += n
    return total