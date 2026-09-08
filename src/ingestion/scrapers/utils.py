import numpy as np
import pandas as pd
from pandas.api.types import infer_dtype

from src.core.constants import NULL_VALUES, SI_NO


def _map_bool(df) -> pd.DataFrame:
    return df.str.strip().str.lower().map(SI_NO)


def _strip_and_replace(df: pd.DataFrame) -> pd.DataFrame:
    obj_cols = [c for c in df.columns if infer_dtype(df[c], skipna=True) == "string"]
    df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())

    no_bool = df.columns.difference(df.select_dtypes("bool").columns)
    df[no_bool] = df[no_bool].replace(NULL_VALUES, np.nan)

    return df


def _limpiar_vacio(df) -> pd.DataFrame:
    return df.str.strip().replace(NULL_VALUES, np.nan)
