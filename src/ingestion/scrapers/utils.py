import numpy as np
import pandas as pd
from pandas.api.types import infer_dtype
import logging

from src.core.constants import NULL_VALUES, SI_NO
from itertools import islice
from pathlib import Path
from dbfread import DBF, exceptions

logger = logging.getLogger(__name__)



def _strip_and_replace(df: pd.DataFrame) -> pd.DataFrame:
    obj_cols = [c for c in df.columns if infer_dtype(df[c], skipna=True) == "string"]
    df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())

    no_bool = df.columns.difference(df.select_dtypes("bool").columns)
    #df[no_bool] = df[no_bool].replace(NULL_VALUES, np.nan)
    df[no_bool] = df[no_bool].mask(df[no_bool].isin(NULL_VALUES))
    
    return df


def _limpiar_vacio(df) -> pd.DataFrame:
    return df.str.strip().replace(NULL_VALUES, np.nan)


def _map_bool(df) -> pd.DataFrame:
    return df.str.strip().str.lower().map(SI_NO)


def _abrir_dbf(p) -> DBF:
    return DBF(
            p,
            encoding="cp850",
            char_decode_errors="ignore",
            load=False,
            ignore_missing_memofile=True,
        )
            

def leer(p) -> pd.DataFrame:
    return pd.DataFrame(iter(_abrir_dbf(p)))


def leer_chunks(p, size: int = 200_000, columnas: list[str] | None = None):
    it = iter(_abrir_dbf(p))
    while lote := list(islice(it, size)):
        yield pd.DataFrame(lote, columns=columnas)  # solo las columnas que se usan


def _chunks_de(rutas, size: int, columnas: list[str] | None):
    for r in rutas:
        print(r)
        try:
            yield from leer_chunks(r, size, columnas)
        except exceptions.DBFNotFound:
            logger.warning(f"Archivo no encontrado: {r}")
        except(OSError, exceptions.DBFError) as e: # type: ignore
            logger.warning(f"Error al leer {r}: {e}")

