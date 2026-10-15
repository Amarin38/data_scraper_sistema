import warnings
from datetime import date

import numpy as np
import pandas as pd
from scipy.stats import poisson
from sqlalchemy.orm import Session
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.core.enums import ModoCargaEnum, TipoPrevisionEnum
from src.repositories.estadisticas import PrevisionRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.repuesto_repository import RepuestoRepository

MIN_MESES_ESTACIONAL = 24
MIN_SALIDAS_ESTACIONAL = 24
NIVEL_NORMAL = 0.95
NIVEL_CRITICO = 0.99


class ComputePrevision:
    def __init__(self):
        self.repo_rep = RepuestoRepository()
        self.repo_ficha = FichaStockRepository()

    def serie_mensual(
        self, db: Session, desde: date = date(2019, 1, 1)
    ) -> pd.DataFrame:
        df = pd.read_sql(
            self.repo_ficha.get_serie_mensual(desde),
            db.connection(),
            parse_dates=["Periodo"],
        )
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
        )

        # 1. Previsión base
        if con_salidas < 6:
            base, metodo = (
                np.repeat(salidas.iloc[-12:].mean(), h),
                TipoPrevisionEnum.PROMEDIO,
            )
        elif len(salidas) / con_salidas > 1.32:
            base, metodo = (
                self.croston(salidas.to_numpy(), h),
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
    def croston(y: np.ndarray, horizonte: int, alpha: float = 0.1) -> np.ndarray:
        nz = np.flatnonzero(y)
        tam, intervalo = y[nz[0]], 1.0
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
        df["StockObjetivo"] = poisson.ppf(nivel, df["Cantidad"]).astype("int64")

        return PrevisionRepository().load_df(
            db, df, ModoCargaEnum.OVERWRITE, commit=False
        )
