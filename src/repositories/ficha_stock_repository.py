from datetime import date

from sqlalchemy import Date, delete, func, select
from sqlalchemy.orm import Session

from src.core.enums import CabecerasEnum, TipoMovEnum
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.repuesto_model import RepuestoModel, codigo_expr
from src.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel
    codigo_col = codigo_expr()

    def delete_by_cabecera(self, db: Session, cabecera: CabecerasEnum) -> int:
        stmt = delete(self.model).where(self.model.Deposito == cabecera)
        return db.execute(stmt).rowcount  # type: ignore

    def get_serie_mensual(self, desde: date):
        mes = func.date_trunc("month", self.model.FechaMov).cast(Date).label("Periodo")
        return (
            select(
                self.model.IDRepuesto,
                mes,
                func.sum(func.abs(self.model.Cantidad)).label("Cantidad"),
            )
            .where(
                self.model.TipoMov == TipoMovEnum.SALIDA,
                self.model.Deposito == CabecerasEnum.MEGABUS,
                self.model.FechaMov >= desde,
                self.model.FechaMov < date.today().replace(day=1),
            )
            .group_by(self.model.IDRepuesto, mes)
        )

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

    def _filtrar(
        self, stmt, deposito, descripcion, codigo, movimiento, fecha_desde, fecha_hasta
    ):
        condiciones_mov = {
            TipoMovEnum.ENTRADA: self.model.TipoMov == TipoMovEnum.ENTRADA,
            TipoMovEnum.SALIDA: self.model.TipoMov == TipoMovEnum.SALIDA,
            TipoMovEnum.TRANSFERENCIA: self.model.DepositoTransfer.is_not(None),
        }

        if deposito:
            stmt = stmt.where(self.model.Deposito == deposito)

        if movimiento:
            condicion = condiciones_mov.get(movimiento)
            if condicion is not None:
                stmt = stmt.where(condicion)

        if descripcion:
            for palabra in descripcion.split():
                stmt = stmt.where(
                    RepuestoModel.Descripcion.icontains(palabra, autoescape=True)
                )

        if codigo:
            stmt = stmt.where(self.codigo_col.ilike(f"%{codigo}%"))

        if fecha_desde:
            stmt = stmt.where(self.model.FechaMov >= fecha_desde)

        if fecha_hasta:
            stmt = stmt.where(self.model.FechaMov <= fecha_hasta)

        return stmt

    def get_ficha(
        self,
        db,
        deposito,
        descripcion,
        codigo,
        movimiento,
        fecha_desde,
        fecha_hasta,
        limit,
        cursor_valor,
        cursor_id,
    ):
        stmt = self._filtrar(
            self._select_base(),
            deposito,
            descripcion,
            codigo,
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
        movimiento,
        fecha_desde,
        fecha_hasta,
    ):
        return self._filtrar(
            self._select_base(),
            deposito,
            descripcion,
            codigo,
            movimiento,
            fecha_desde,
            fecha_hasta,
        )
