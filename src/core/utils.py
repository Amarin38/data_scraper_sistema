import logging
import os
import shutil
import struct
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from itertools import islice

import numpy as np
import pandas as pd
from dbfread import DBF, FieldParser, exceptions
from numpy.lib import recfunctions as rfn

logger = logging.getLogger(__name__)

TMP_DIR = None  # ej: "/mnt/HDD/tmp" si /tmp es tmpfs y el DBF es grande
ENCODING = "cp850"


class ParserNulos(FieldParser):
    def parse(self, field, data):
        if field.type in "NFD":
            data = data.strip(b"\x00 ")
            if not data:
                return None
        return super().parse(field, data)


def _abrir_dbf(p) -> DBF:
    return DBF(
        p,
        encoding=ENCODING,
        char_decode_errors="ignore",
        load=False,
        ignore_missing_memofile=True,
        parserclass=ParserNulos,
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


# ---------------------------------------------------------------- lector rápido


def _campos(p):
    """Cabecera DBF: (largo_cabecera, largo_registro, [(nombre, tipo, largo, decimales, offset)])."""
    with open(p, "rb") as fh:
        lh, lr = struct.unpack("<HH", fh.read(32)[8:12])
        campos, off = [], 1  # el byte 0 del registro es la marca de borrado
        while True:
            d = fh.read(32)
            if not d or d[0] == 0x0D:
                break
            nombre = d[:11].split(b"\x00")[0].decode("ascii", "ignore")
            campos.append((nombre, chr(d[11]), d[16], d[17], off))
            off += d[16]
    return lh, lr, campos


def _convertir(arr: np.ndarray, tipo: str, dec: int) -> pd.Series:
    s = pd.Series(arr)  # bytes (object); numpy ya recortó los \x00 finales
    if tipo == "C":
        return s.str.decode(ENCODING, errors="ignore").str.rstrip(" \x00")

    txt = s.str.decode("ascii", errors="ignore").str.strip(" \x00")

    if tipo in "NF":
        v = pd.to_numeric(txt.str.replace(",", ".", regex=False), errors="coerce")
        if dec == 0:
            try:
                return v.astype("Int64")
            except TypeError, ValueError:
                return v
        return v

    if tipo == "D":
        d = pd.to_datetime(txt, format="%Y%m%d", errors="coerce")
        d = d.where(d.dt.year >= 1900)  # fuera de rango razonable -> NaT
        return d.dt.strftime("%Y-%m-%d").astype(object).where(d.notna(), None)

    if tipo == "L":
        return txt.map(
            {
                "T": True,
                "t": True,
                "Y": True,
                "y": True,
                "F": False,
                "f": False,
                "N": False,
                "n": False,
            }
        )

    return pd.Series([None] * len(s), dtype=object)  # memo y otros: None


@dataclass
class BloqueDBF:
    """Bytes crudos de un chunk (solo las columnas usadas). Barato de serializar:
    la conversión a DataFrame se hace en quien lo consume (el worker)."""

    datos: np.ndarray
    campos: list  # [(nombre, tipo, decimales)]
    columnas: list[str] | None

    def a_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                nom: _convertir(self.datos[nom], tipo, dec)
                for nom, tipo, dec in self.campos
            }
        )
        if self.columnas is not None:
            df = df.reindex(columns=self.columnas)
        return df.dropna(how="all")


def leer_chunks_crudos(p, size: int = 200_000, columnas: list[str] | None = None):
    """Lee el DBF en bloques binarios con numpy, sin convertir. Emite BloqueDBF."""
    lh, lr, campos = _campos(p)
    n = (os.path.getsize(p) - lh) // lr

    # marcas \x1a a mitad de archivo: se leen como registros normales
    # (igual que la copia corregida de _dbf_reparado), solo se avisa.
    malos = np.flatnonzero(
        np.memmap(p, dtype=np.uint8, mode="r")[lh : lh + n * lr : lr] == 0x1A
    )
    if len(malos):
        logger.warning(
            "%s: %d marca(s) EOF a mitad de archivo (registros %s); se ignoran",
            p,
            len(malos),
            malos[:5].tolist(),
        )

    usar = [c for c in campos if columnas is None or c[0] in columnas]
    nombres = [c[0] for c in usar]
    meta = [(c[0], c[1], c[3]) for c in usar]
    dt = np.dtype(
        {
            "names": ["_b"] + nombres,
            "formats": ["S1"] + [f"S{c[2]}" for c in usar],
            "offsets": [0] + [c[4] for c in usar],
            "itemsize": lr,
        }
    )

    total = 0
    for ini in range(0, n, size):
        cnt = min(size, n - ini)
        a = np.fromfile(p, dtype=dt, count=cnt, offset=lh + ini * lr)
        a = a[(a["_b"] != b"*") & (a["_b"] != b"\x00")]  # borrado o vacío
        total += len(a)
        if not len(a):
            continue
        # copia compacta: solo las columnas usadas (el pickle pesa mucho menos)
        yield BloqueDBF(rfn.repack_fields(a[nombres]), meta, columnas)

    logger.debug("%s: leídas %d", p, total)


def leer_chunks(p, size: int = 200_000, columnas: list[str] | None = None):
    """Igual que antes: emite DataFrames (convierte en este proceso)."""
    for bloque in leer_chunks_crudos(p, size, columnas):
        df = bloque.a_df()
        if len(df):
            yield df


def leer_chunks_dbfread(p, size: int = 200_000, columnas: list[str] | None = None):
    """Versión lenta original, para comparar."""
    with _dbf_reparado(p) as (ruta, esperadas):
        it = iter(_abrir_dbf(ruta))
        total = 0

        while lote := list(islice(it, size)):
            total += len(lote)
            df = pd.DataFrame(lote, columns=columnas).dropna(how="all")
            yield df

        if total != esperadas:
            logger.warning("%s: leídas %d, esperadas %d", p, total, esperadas)


def _chunks_de(rutas, size: int, columnas: list[str] | None, crudo: bool = False):
    leer_fn = leer_chunks_crudos if crudo else leer_chunks
    for r in rutas:
        print(r)
        try:
            yield from leer_fn(r, size, columnas)
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
