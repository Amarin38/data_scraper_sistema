from datetime import date
import logging
import os
import shutil
import struct
import tempfile
from contextlib import contextmanager
from itertools import islice

import numpy as np
import pandas as pd
from dbfread import DBF, exceptions

logger = logging.getLogger(__name__)

TMP_DIR = None  # ej: "/mnt/HDD/tmp" si /tmp es tmpfs y el DBF es grande


def _abrir_dbf(p) -> DBF:
    return DBF(
        p,
        encoding="cp850",
        char_decode_errors="ignore",
        load=False,
        ignore_missing_memofile=True,
    )


def _inspeccionar(p):
    """Posiciones de registros con marca \\x1a, registros por tamaño y borrados."""
    with open(p, "rb") as fh:
        lh, lr = struct.unpack("<HH", fh.read(32)[8:12])
    n = (os.path.getsize(p) - lh) // lr
    mm = np.memmap(p, dtype=np.uint8, mode="r")
    marcas = mm[lh : lh + n * lr : lr]  # primer byte de cada registro
    malos = np.flatnonzero(marcas == 0x1A)
    borrados = int((marcas == 0x2A).sum())  # '*'
    del marcas, mm
    return malos, n, borrados, lh, lr


@contextmanager
def _dbf_reparado(p):
    """Devuelve (ruta_a_leer, filas_esperadas). Si hay \\x1a a mitad de archivo, lee una copia corregida."""
    malos, n, borrados, lh, lr = _inspeccionar(p)
    esperadas = n - borrados

    if len(malos) == 0:
        yield p, esperadas
        return

    logger.warning(
        "%s: %d marca(s) EOF a mitad de archivo (registros %s); se lee copia corregida",
        p,
        len(malos),
        malos[:5].tolist(),
    )
    fd, tmp = tempfile.mkstemp(suffix=".dbf", dir=TMP_DIR)
    os.close(fd)
    try:
        shutil.copyfile(p, tmp)
        with open(tmp, "r+b") as fh:
            for i in malos:
                fh.seek(lh + int(i) * lr)
                fh.write(b" ")
        yield tmp, esperadas
    finally:
        os.remove(tmp)


def leer(p) -> pd.DataFrame:
    with _dbf_reparado(p) as (ruta, _):
        return pd.DataFrame(iter(_abrir_dbf(ruta)))


def leer_chunks(p, size: int = 200_000, columnas: list[str] | None = None):
    with _dbf_reparado(p) as (ruta, esperadas):
        it = iter(_abrir_dbf(ruta))
        total = 0
        while lote := list(islice(it, size)):
            total += len(lote)
            yield pd.DataFrame(lote, columns=columnas)
        if total != esperadas:
            logger.warning("%s: leídas %d, esperadas %d", p, total, esperadas)


def _chunks_de(rutas, size: int, columnas: list[str] | None):
    for r in rutas:
        print(r)
        try:
            yield from leer_chunks(r, size, columnas)
        except exceptions.DBFNotFound, FileNotFoundError:
            logger.warning(f"Archivo no encontrado: {r}")
        except OSError as e:
            logger.warning("no se pudo leer %s: %s", r, e)


def arreglar_fechas(df: pd.DataFrame, col: str) -> tuple[pd.DataFrame, pd.Series]:
    FECHA_MINIMA = pd.Timestamp("1990-01-01")
    FECHA_MAXIMA = pd.Timestamp(date.today())

    fecha = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
    mascara = fecha.notna() & (fecha >= FECHA_MINIMA) & (fecha <= FECHA_MAXIMA)
    return df.loc[mascara].copy(), fecha[mascara].dt.strftime("%Y-%m-%d")
