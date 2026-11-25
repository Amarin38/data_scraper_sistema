import calendar
import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy.stats import nbinom, poisson
from sqlalchemy.orm import Session
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from shared.core.enums import ModoCargaEnum, TipoPrevisionEnum
from shared.db.models.repuesto_model import RepuestoModel
from shared.repositories.estadisticas import PrevisionRepository
from shared.repositories.existencia_stock_repository import ExistenciaStockRepository
from shared.repositories.ficha_stock_repository import FichaStockRepository
from shared.repositories.repuesto_repository import RepuestoRepository

MIN_MESES_ESTACIONAL = 24
MIN_SALIDAS_ESTACIONAL = 24
MIN_SALIDAS_VENTANA = 3
NIVEL_NORMAL = 0.95
NIVEL_CRITICO = 0.99
PLAZO_REPOSICION_MESES = 2
HORIZONTE_SIMULADO = 12
MESES_HISTORIA = 24
VENTANA_CROSTON = 24
MESES_SIN_SALIDAS = 6
UMBRAL_PICO = 10


def desde_defecto() -> date:
    """Primer mes de la ventana de consumo: hoy menos MESES_HISTORIA, al día 1."""
    return date.today().replace(day=1) - relativedelta(months=MESES_HISTORIA)


class ComputePrevision:
    def __init__(self):
        self.repo_rep = RepuestoRepository()
        self.repo_ficha = FichaStockRepository()

    def serie_mensual(self, db: Session, desde: date | None = None) -> pd.DataFrame:
        desde = desde or desde_defecto()
        df = pd.read_sql(
            self.repo_ficha.get_serie_mensual(desde),
            db.connection(),
            parse_dates=["Periodo"],
        )
        db.commit()
        df["Cantidad"] = df["Cantidad"].astype(float)

        return df.pivot_table(
            index="Periodo", columns="IDRepuesto", values="Cantidad", fill_value=0
        ).asfreq("MS", fill_value=0)

    @staticmethod
    def indices_estacionales(salidas: pd.Series, k: float = 3.0) -> np.ndarray:
        """Índice por mes del año (posición 0 = enero), encogido hacia 1 según años de historia."""
        media = salidas.mean()
        if media == 0:
            return np.ones(12)
        por_mes = salidas.groupby(salidas.index.month).mean() / media  # type:ignore
        n = (salidas > 0).sum()
        w = n / (n + k)  # 12 meses con salidas
        return (1 + w * (por_mes - 1)).reindex(range(1, 13), fill_value=1.0).to_numpy()

    def compute_prevision(
        self, salidas: pd.Series, h: int = 6
    ) -> tuple[np.ndarray, TipoPrevisionEnum]:
        con_salidas = (salidas > 0).sum()
        estacional = (
            len(salidas) >= MIN_MESES_ESTACIONAL
            and con_salidas >= MIN_SALIDAS_ESTACIONAL
            and salidas.max() <= UMBRAL_PICO * salidas[salidas > 0].median()
        )

        if con_salidas < 6:
            base, metodo = (
                np.repeat(salidas.iloc[-12:].mean(), h),
                TipoPrevisionEnum.PROMEDIO,
            )
        elif len(salidas) / con_salidas > 1.32:
            base, metodo = (
                self.croston(salidas.iloc[-VENTANA_CROSTON:].to_numpy(), h),
                TipoPrevisionEnum.CROSTON,
            )
        else:
            try:
                modelo = ExponentialSmoothing(
                    salidas,
                    trend="add",
                    damped_trend=True,
                    seasonal="add" if estacional else None,
                    seasonal_periods=12 if estacional else None,
                    initialization_method="heuristic",
                ).fit(use_brute=False)

                return modelo.forecast(h).clip(
                    lower=0
                ).to_numpy(), TipoPrevisionEnum.EXPONENCIAL
            except Exception:
                base, metodo = (
                    np.repeat(salidas.iloc[-12:].mean(), h),
                    TipoPrevisionEnum.PROMEDIO,
                )

        if estacional:
            meses_futuros = [
                (salidas.index[-1] + pd.offsets.MonthBegin(i)).month
                for i in range(1, h + 1)
            ]
            base = (
                base * self.indices_estacionales(salidas)[np.array(meses_futuros) - 1]
            )

        return base, metodo

    @staticmethod
    def stock_objetivo(
        mensual, dispersion, nivel, plazo: int = PLAZO_REPOSICION_MESES
    ) -> np.ndarray:
        """Cuantil `nivel` de la demanda del plazo: binomial negativa con media =
        previsión × plazo y varianza = dispersión × media. Poisson si dispersión ≤ 1."""
        mu = np.asarray(mensual, dtype=float) * plazo
        d = np.asarray(dispersion, dtype=float)
        sobre = d > 1.0001
        d = np.where(sobre, d, 2.0)  # evita dividir por cero donde no se usa
        with np.errstate(all="ignore"):
            q = np.where(
                sobre,
                nbinom.ppf(nivel, mu / (d - 1), 1 / d),
                poisson.ppf(nivel, mu),
            )
        return np.where(mu > 0, np.nan_to_num(q), 0).astype("int64")

    @staticmethod
    def croston(y: np.ndarray, horizonte: int, alpha: float = 0.1) -> np.ndarray:
        nz = np.flatnonzero(y)
        if nz.size == 0 or nz[-1] < len(y) - MESES_SIN_SALIDAS:
            return np.zeros(horizonte)

        tam = y[nz].mean()
        intervalo = len(y) / len(nz)
        ultimo = nz[0]

        for i in nz[1:]:
            tam += alpha * (y[i] - tam)
            intervalo += alpha * ((i - ultimo) - intervalo)
            ultimo = i

        return np.repeat(tam / intervalo, horizonte)

    def calcular_prevision(
        self,
        db: Session,
        horizonte: int = 6,
        meses_activo: int = 24,
        meses_cobertura: int = 12,
    ) -> int:

        repuesto_repo = RepuestoRepository()
        series = self.serie_mensual(db)

        # solo repuestos con alguna salida en los últimos `meses_activo` meses
        activos = series.columns[series.iloc[-meses_activo:].sum() > 0]
        futuro = pd.date_range(
            series.index[-1] + pd.offsets.MonthBegin(), periods=horizonte, freq="MS"
        )

        filas = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # avisos de convergencia de statsmodels
            for id_repuesto in activos:
                valores, metodo = self.compute_prevision(series[id_repuesto], horizonte)
                filas += [
                    (id_repuesto, p.date(), float(v), metodo)
                    for p, v in zip(futuro, valores)
                ]

        df = pd.DataFrame(
            filas, columns=["IDRepuesto", "Periodo", "Cantidad", "Metodo"]
        )
        df["FechaCalculo"] = date.today()

        criticos = repuesto_repo.get_criticos(db)
        nivel = np.where(df["IDRepuesto"].isin(criticos), NIVEL_CRITICO, NIVEL_NORMAL)
        media = series.mean()
        dispersion = (series.var(ddof=0) / media).where(media > 0, 1.0)
        df["StockObjetivo"] = self.stock_objetivo(
            df["Cantidad"], df["IDRepuesto"].map(dispersion), nivel
        )

        return PrevisionRepository().load_df(
            db, df, ModoCargaEnum.OVERWRITE, commit=False
        )

    def prevision_simulada(
        self,
        db: Session,
        id_repuesto: int,
        desde: date | None = None,
        hasta: date | None = None,
        horizonte: int = HORIZONTE_SIMULADO,
    ) -> list[dict]:
        """Recalcula la previsión de UN repuesto con el consumo recortado a [desde, hasta].
        Exploratorio: no guarda nada. Mismo formato que PrevisionRepository.listar_por_repuesto."""
        ultimo = (pd.Timestamp(date.today()).to_period("M") - 1).to_timestamp()
        ini = pd.Timestamp(desde or desde_defecto()).to_period("M").to_timestamp()
        fin = (
            min(pd.Timestamp(hasta).to_period("M").to_timestamp(), ultimo)
            if hasta
            else ultimo
        )
        if ini > fin:
            return []

        df = pd.read_sql(
            self.repo_ficha.get_serie_mensual(ini.date(), id_repuesto),
            db.connection(),
            parse_dates=["Periodo"],
        )
        db.commit()

        por_mes = dict(zip(df["Periodo"], df["Cantidad"].astype(float)))
        meses = pd.date_range(ini, fin, freq="MS")
        serie = pd.Series([por_mes.get(m, 0.0) for m in meses], index=meses)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            valores, _ = self.compute_prevision(serie, horizonte)
        futuro = pd.date_range(
            fin + pd.offsets.MonthBegin(), periods=horizonte, freq="MS"
        )

        filas = [
            {
                "IDRepuesto": id_repuesto,
                "Mes": m.strftime("%Y-%m"),
                "Cantidad": round(float(v), 2),
                "Tipo": "Consumo",
            }
            for m, v in serie.items()
        ]
        filas += [
            {
                "IDRepuesto": id_repuesto,
                "Mes": m.strftime("%Y-%m"),
                "Cantidad": round(float(v), 2),
                "Tipo": "Prevision",
            }
            for m, v in zip(futuro, valores)
        ]
        return filas

    @staticmethod
    def fecha_agotamiento(stock: float, prev: list[dict], base: date) -> date | None:
        """Día estimado en que el stock llega a 0 consumiendo lo previsto.
        `base` = fecha del stock. Devuelve `base` si ya no hay, None si no se agota."""
        if stock <= 0:
            return base
        restante = stock
        for f in prev:
            y, m = map(int, f["Mes"].split("-"))
            if (y, m) < (base.year, base.month):
                continue
            dim = calendar.monthrange(y, m)[1]
            q = float(f["Cantidad"])
            if (y, m) == (base.year, base.month):
                dias = dim - base.day + 1  # lo ya consumido este mes está en el stock
                inicio = base
                q *= dias / dim
            else:
                dias, inicio = dim, date(y, m, 1)
            if q <= 0:
                continue
            if q >= restante:
                return inicio + timedelta(days=round(dias * restante / q))
            restante -= q
        return None

    def cobertura(self, db: Session, id_repuesto: int, filas: list[dict]) -> dict:
        prev = sorted(
            (f for f in filas if f["Tipo"] == "Prevision"), key=lambda f: f["Mes"]
        )
        mensual = [float(f["Cantidad"]) for f in prev]

        rep = db.get(RepuestoModel, id_repuesto)
        nivel = NIVEL_CRITICO if rep is not None and rep.Critico else NIVEL_NORMAL

        def objetivo(n: int) -> int | None:
            if len(mensual) < n:
                return None
            total = sum(mensual[:n])
            return int(poisson.ppf(nivel, total)) if total > 0 else 0

        stock, fecha = ExistenciaStockRepository().stock_actual(db, id_repuesto)
        base = fecha or date.today()
        cubiertos = sum(
            1
            for f in prev
            if tuple(map(int, f["Mes"].split("-"))) >= (base.year, base.month)
        )
        agotamiento = (
            self.fecha_agotamiento(float(stock), prev, base)
            if stock is not None
            else None
        )
        return {
            "Stock": stock,
            "FechaStock": fecha,
            "Nivel": nivel,
            "Objetivo3": objetivo(3),
            "Objetivo6": objetivo(6),
            "Objetivo12": objetivo(12),
            "MesesCubiertos": cubiertos,
            "Agotamiento": agotamiento,
        }
