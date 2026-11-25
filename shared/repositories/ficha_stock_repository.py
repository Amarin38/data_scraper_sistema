from datetime import date

from sqlalchemy import Date, and_, delete, func, or_, select, true
from sqlalchemy.orm import Session

from shared.core.enums import CabecerasEnum, TipoMovEnum
from shared.core.paths import ArchivosDatosEnum
from shared.db.models.ficha_stock_model import FichaStockModel
from shared.db.models.repuesto_model import RepuestoModel, codigo_expr
from shared.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel
    codigo_col = codigo_expr()

    def delete_by_cabecera(
        self, db: Session, cabecera: CabecerasEnum, parcial: bool = False
    ) -> int:
        stmt = delete(self.model).where(self.model.Deposito == cabecera)

        if parcial:
            stmt = stmt.where(self.model.Origen == ArchivosDatosEnum.FICART.value)

        return db.execute(stmt).rowcount  # type: ignore

    def get_serie_mensual(self, desde: date, id_repuesto: int | None = None):
        mes = func.date_trunc("month", self.model.FechaMov).cast(Date).label("Periodo")
        stmt = select(
            self.model.IDRepuesto,
            mes,
            func.sum(func.abs(self.model.Cantidad)).label("Cantidad"),
        ).where(
            self.model.TipoMov == TipoMovEnum.SALIDA,
            self.model.Deposito == CabecerasEnum.MEGABUS,
            self.model.FechaMov >= desde,
            self.model.FechaMov < date.today().replace(day=1),
        )
        if id_repuesto is not None:
            stmt = stmt.where(self.model.IDRepuesto == id_repuesto)
        return stmt.group_by(self.model.IDRepuesto, mes)

    def _select_base(self):
        return select(
            self.model.IDFichaStock,
            self.model.IDRepuesto,
            self.codigo_col.label("Codigo"),
            RepuestoModel.Descripcion,
            self.model.FechaMov,
            self.model.Deposito,
            self.model.TipoMov,
            self.model.Cantidad,
            self.model.PrecioUnitario,
            self.model.Interno,
            self.model.TipoUsuario,
            self.model.DepositoTransfer,
        ).join(RepuestoModel, RepuestoModel.IDRepuesto == self.model.IDRepuesto)

    # --- condiciones, separadas por tabla ---------------------------------

    def _cond_repuesto(self, descripcion, codigo) -> list:
        condiciones = []
        if descripcion:
            condiciones.extend(
                RepuestoModel.Descripcion.icontains(palabra, autoescape=True)
                for palabra in descripcion.split()
            )
        if codigo:
            condiciones.append(self.codigo_col.ilike(f"%{codigo}%"))
        return condiciones

    def _cond_mov(
        self, deposito, interno, movimiento, fecha_desde, fecha_hasta
    ) -> list:
        condiciones_mov = {
            TipoMovEnum.ENTRADA: self.model.TipoMov == TipoMovEnum.ENTRADA,
            TipoMovEnum.SALIDA: self.model.TipoMov == TipoMovEnum.SALIDA,
            TipoMovEnum.TRANSFERENCIA: self.model.DepositoTransfer.is_not(None),
        }
        condiciones = []
        if deposito:
            condiciones.append(self.model.Deposito == deposito)
        if movimiento:
            condicion = condiciones_mov.get(movimiento)
            if condicion is not None:
                condiciones.append(condicion)
        if interno:
            condiciones.append(self.model.Interno == interno)
        if fecha_desde:
            condiciones.append(self.model.FechaMov >= fecha_desde)
        if fecha_hasta:
            condiciones.append(self.model.FechaMov <= fecha_hasta)
        return condiciones

    def _filtrar(
        self,
        stmt,
        deposito,
        descripcion,
        codigo,
        interno,
        movimiento,
        fecha_desde,
        fecha_hasta,
    ):
        condiciones = self._cond_mov(
            deposito, interno, movimiento, fecha_desde, fecha_hasta
        ) + self._cond_repuesto(descripcion, codigo)
        return stmt.where(*condiciones) if condiciones else stmt

    # --- búsqueda por código: últimos N movimientos de cada repuesto ------

    def _ids_candidatos(
        self,
        deposito,
        descripcion,
        codigo,
        interno,
        movimiento,
        fecha_desde,
        fecha_hasta,
        limit,
        cursor_valor,
        cursor_id,
    ):
        reps = (
            select(RepuestoModel.IDRepuesto)
            .where(*self._cond_repuesto(descripcion, codigo))
            .subquery()
        )

        interior = select(self.model.IDFichaStock, self.model.FechaMov).where(
            self.model.IDRepuesto == reps.c.IDRepuesto,
            *self._cond_mov(deposito, interno, movimiento, fecha_desde, fecha_hasta),
        )

        # mismo orden que la paginación: FechaMov DESC, IDFichaStock ASC
        if cursor_id is not None and cursor_valor is not None:
            interior = interior.where(
                or_(
                    self.model.FechaMov < cursor_valor,
                    and_(
                        self.model.FechaMov == cursor_valor,
                        self.model.IDFichaStock > cursor_id,
                    ),
                )
            )

        ult = (
            interior.order_by(self.model.FechaMov.desc(), self.model.IDFichaStock.asc())
            .limit(limit + 1)
            .lateral("ult")
        )

        return select(ult.c.IDFichaStock).select_from(reps.join(ult, true()))

    def get_ficha(
        self,
        db,
        deposito,
        descripcion,
        codigo,
        interno,
        movimiento,
        fecha_desde,
        fecha_hasta,
        limit,
        cursor_valor,
        cursor_id,
    ):
        if codigo:
            # los filtros ya se aplicaron dentro del LATERAL
            candidatos = self._ids_candidatos(
                deposito,
                descripcion,
                codigo,
                interno,
                movimiento,
                fecha_desde,
                fecha_hasta,
                limit,
                cursor_valor,
                cursor_id,
            )
            stmt = self._select_base().where(self.model.IDFichaStock.in_(candidatos))
        else:
            stmt = self._filtrar(
                self._select_base(),
                deposito,
                descripcion,
                codigo,
                interno,
                movimiento,
                fecha_desde,
                fecha_hasta,
            )

        return self._paginar(
            db,
            stmt,
            limit,
            pk_col=("IDFichaStock", self.model.IDFichaStock),
            valor_col=("FechaMov", self.model.FechaMov),
            cursor=(cursor_id, cursor_valor),
        )

    def stmt_exportar(
        self,
        deposito,
        descripcion,
        codigo,
        interno,
        movimiento,
        fecha_desde,
        fecha_hasta,
    ):
        return self._filtrar(
            self._select_base(),
            deposito,
            descripcion,
            codigo,
            interno,
            movimiento,
            fecha_desde,
            fecha_hasta,
        )
