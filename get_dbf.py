import pandas as pd
from dbfread import DBF

from constants import (
    DROP_COLS,
    RENAME_COLS,
    RENAME_MOV,
    RUTA_SERVER_FICANT,
    RUTA_SERVER_FICANT1,
    RUTA_SERVER_FICART,
    SORT_COLS,
    TIPOS_DATOS_COLS,
    TIPOS_DEPOS_COLS,
)


def leer(p):
    return pd.DataFrame(
        iter(DBF(p, encoding="cp850", char_decode_errors="ignore", load=False))
    )


def inspeccionar_unico(rutas: list):
    dfs_finales = []

    for r in rutas:
        print(r)
        dfs_finales.append(leer(r))

    df = pd.concat(dfs_finales, ignore_index=False)
    df = df.sort_values(SORT_COLS)
    df = df.rename(columns=RENAME_COLS)
    df["TipoMov"] = df["TipoMov"].replace(RENAME_MOV)

    df = df.astype(TIPOS_DATOS_COLS).astype(TIPOS_DEPOS_COLS)
    df = df.drop(columns=DROP_COLS)
    df["FechaMov"] = pd.to_datetime(df["FechaMov"], errors="coerce")
    df = df[(df.Familia != 0) &
            (df.Deposito == 9)]

    df.loc[df["TipoMov"].isin(["Salida", "Transferencia Deposito"]) , "Cantidad"] *= -1 # type: ignore

    df.to_csv("dbfs/FICHA_STOCK.csv", index=False)


if __name__ == "__main__":
    # inspeccionar_unico([RUTA_SERVER_FICANT, RUTA_SERVER_FICANT1, RUTA_SERVER_FICART])
    df = pd.read_csv("dbfs/FICHA_STOCK.csv")
    df = df[(df.Familia == 11) &
            (df.Articulo == 19)]

    stock_actual = df["Cantidad"].sum()


    print(df)
    print(stock_actual)
