from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from sqlalchemy import Select, func, literal, select, case, or_

from src.core.enums import CabecerasEnum
from src.db.models.estadisticas.conteo_stock_model import ConteoStockModel
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.estadisticas.indice_consumo_model import IndiceConsumoModel
from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.db.models.repuesto_model import RepuestoModel
from src.db.views.consumo_mensual import t as consumo_mensual
from src.repositories.base_repository import BaseRepository

rep_model = RepuestoModel


class IndiceConsumoRepository(BaseRepository[IndiceConsumoModel]):
    model = IndiceConsumoModel

    def listar_por_repuesto(self, db, id_repuesto: int):
        type SelectIndice = Select[
            int, str, str, str, CabecerasEnum, Decimal, Decimal, Decimal, date
        ]

        stmt: SelectIndice = (
            select(
                self.model.IDRepuesto,
                rep_model.Familia,
                rep_model.Articulo,
                rep_model.Descripcion,
                self.model.Deposito,
                self.model.Indice,
                self.model.IndiceGlobal,
                self.model.IndiceRelativo,
                self.model.FechaIndice,
            )
            .join(rep_model, rep_model.IDRepuesto == self.model.IDRepuesto)
            .where(self.model.IDRepuesto == id_repuesto)
            .order_by(rep_model.Descripcion)
        )

        return [dict(r) for r in db.execute(stmt).mappings().all()]


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel

    def listar_por_repuesto(self, db, id_repuesto: int):
        hoy_mes = date.today().replace(day=1)
        desde = hoy_mes - relativedelta(months=24)

        consumo = select(
            consumo_mensual.c.IDRepuesto,
            func.to_char(consumo_mensual.c.mes, "YYYY-MM").label("Mes"),
            consumo_mensual.c.consumo.label("Cantidad"),
            literal("Consumo").label("Tipo"),
        ).where(
            consumo_mensual.c.IDRepuesto == id_repuesto,
            consumo_mensual.c.mes >= desde,
            consumo_mensual.c.mes < hoy_mes,
        )

        prev = select(
            self.model.IDRepuesto,
            func.to_char(self.model.Periodo, "YYYY-MM").label("Mes"),
            self.model.Cantidad,
            literal("Prevision").label("Tipo"),
        ).where(self.model.IDRepuesto == id_repuesto)

        stmt = consumo.union_all(prev)
        return [dict(f) for f in db.execute(stmt).mappings().all()]


class DuracionRepuestosRepository(BaseRepository[DuracionRepuestosModel]):
    model = DuracionRepuestosModel

    def listar_por_repuesto(
        self,
        db,
        id_repuesto: int,
        patentado_desde: date | None = None,
        patentado_hasta: date | None = None,
    ):
        # solo reposiciones: el primer período arranca en el patentado y no es confiable
        filtros = [self.model.IDRepuesto == id_repuesto, self.model.Cambio > 1]
        if patentado_desde:
            filtros.append(self.model.FechaPatentado >= patentado_desde)
        if patentado_hasta:
            filtros.append(self.model.FechaPatentado <= patentado_hasta)

        # la observación termina en el último cambio registrado del repuesto:
        # si el código se dejó de usar, las piezas "vigentes" no están en uso de verdad
        ultimo = (
            select(func.max(self.model.FechaCambio))
            .where(self.model.IDRepuesto == id_repuesto, ~self.model.Censurado)
            .scalar_subquery()
        )
        dias = case(
            (
                self.model.Censurado,
                func.least(self.model.DuracionDias, ultimo - self.model.FechaInicio),
            ),
            else_=self.model.DuracionDias,
        )
        filtros.append(or_(~self.model.Censurado, ultimo > self.model.FechaInicio))

        fallas = func.count().filter(~self.model.Censurado)

        fila = (
            db.execute(
                select(
                    (
                        func.avg(self.model.DuracionDias).filter(~self.model.Censurado)
                        / 365.0
                    ).label("Media"),
                    (
                        func.stddev_samp(self.model.DuracionDias).filter(
                            ~self.model.Censurado
                        )
                        / 365.0
                    ).label("Desvio"),
                    fallas.label("N"),
                    (func.sum(dias) / 365.0 / func.nullif(fallas, 0)).label(
                        "Exposicion"
                    ),
                    ultimo.label("UltimoCambio"),
                ).where(*filtros)
            )
            .mappings()
            .one()
        )

        d = dias.label("d")
        filas = db.execute(
            select(
                d,
                func.count().filter(~self.model.Censurado),
                func.count().filter(self.model.Censurado),
            )
            .where(*filtros)
            .group_by(d)
            .order_by(d)
        ).all()

        resultado = dict(fila)
        resultado.update(self.kaplan_meier(filas))
        return resultado

    def kaplan_meier(self, filas):
        """filas: (dias, fallas, censuradas) ordenadas por dias. Devuelve Mediana, P25 y Curva (años)."""
        en_riesgo = sum(d + c for _, d, c in filas)
        s = 1.0
        mediana = None
        p25 = None
        curva = [[0.0, 1.0]]
        t_final = 0

        for t, d, c in filas:
            if d:
                s *= 1 - d / en_riesgo
                curva.append([t / 365, s])
                if p25 is None and s <= 0.75:
                    p25 = t / 365
                if mediana is None and s <= 0.5:
                    mediana = t / 365
            en_riesgo -= d + c
            t_final = t

        if len(curva) < 2:
            return {"Mediana": None, "P25": None, "Curva": []}

        curva.append([t_final / 365, s])  # sigue plana hasta la última observación
        return {
            "Mediana": mediana,
            "P25": p25,
            "Curva": [[round(x, 3), round(y, 4)] for x, y in curva],
        }


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
