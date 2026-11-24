import numpy as np
import pandas as pd
from sqlalchemy import text

from src.db.session import engine

df = pd.read_sql(
    text('SELECT "IDRepuesto" AS id, mes, consumo FROM consumo_mensual'),
    engine,
    parse_dates=["mes"],
)
serie = df.pivot_table(
    index="mes", columns="id", values="consumo", aggfunc="sum", fill_value=0.0
)
serie = serie.asfreq("MS", fill_value=0.0)
serie = serie[
    serie.index < pd.Timestamp.today().to_period("M").to_timestamp()
]  # sin mes en curso


def croston(y, alpha=0.1):
    nz = np.flatnonzero(y)
    if nz.size == 0:
        return 0.0
    tam, intervalo, ult = y[nz].mean(), len(y) / len(nz), nz[0]
    for i in nz[1:]:
        tam += alpha * (y[i] - tam)
        intervalo += alpha * ((i - ult) - intervalo)
        ult = i
    return tam / intervalo


def prever(y, ventana, min_sal):
    if ventana is None:
        return croston(y)
    rec = y[-ventana:]
    return croston(rec if (rec > 0).sum() >= min_sal else y)


HOLD = 6
variantes = {
    "24m": (None, 0),
    "12m": (12, 0),
    "12m, guarda<2": (12, 2),
    "12m, guarda<3": (12, 3),
    "12m, guarda<4": (12, 4),
}
acum = {k: dict(err=0.0, pred=0.0, inflados=0) for k in variantes}
real_total, n_items = 0.0, 0

for k in (0, 3, 6):  # tres cortes distintos
    e = len(serie) - HOLD - k
    if e < 18:
        continue
    hist, fut = serie.iloc[max(0, e - 24) : e], serie.iloc[e : e + HOLD]
    for col in serie.columns:
        y = hist[col].to_numpy()
        con = (y > 0).sum()
        if con < 6 or len(y) / con <= 1.32:  # misma regla que usa Croston en el código
            continue
        real = fut[col].mean()
        n_items += 1
        real_total += real
        for nombre, (v, m) in variantes.items():
            p = prever(y, v, m)
            acum[nombre]["err"] += abs(p - real)
            acum[nombre]["pred"] += p
            acum[nombre]["inflados"] += p > 3 * max(real, 0.5)

print(f"repuestos evaluados (suma de cortes): {n_items}")
print(f"{'variante':18} {'error abs.':>11} {'sesgo':>7} {'inflados x3':>12}")
for nombre, a in acum.items():
    print(
        f"{nombre:18} {a['err'] / real_total:11.2f} {a['pred'] / real_total:7.2f} {a['inflados']:12d}"
    )
