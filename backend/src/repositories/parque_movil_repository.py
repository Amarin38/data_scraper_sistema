import pandas as pd
from sqlalchemy import Select, String, cast, select
from sqlalchemy.orm import Session

from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel
from src.db.models.parque_movil_historial_model import ParqueMovilHistorialModel
from src.db.models.parque_movil_model import ParqueMovilModel
from src.repositories.base_repository import BaseRepository


class ParqueMovilRepository(BaseRepository[ParqueMovilModel]):
    model = ParqueMovilModel


class ParqueMovilHistorialRepository(BaseRepository[ParqueMovilHistorialModel]):
    model = ParqueMovilHistorialModel
    chasis_marca = ChasisMarcaModel
    chasis_modelo = ChasisModeloModel
    motor_marca = MotorMarcaModel
    motor_modelo = MotorModeloModel

    def listar_internos_patentes(self, db: Session) -> pd.DataFrame:
        stmt = select(
            self.model.FechaHistorial,
            self.model.Interno,
            self.model.Dominio,
            self.model.FechaPatentado,
        ).order_by(self.model.FechaHistorial, self.model.Interno, self.model.Dominio)

        return pd.read_sql(stmt, db.bind)  # type: ignore

    def _select_base(self):
        return (
            select(
                self.model.IDParqueMovilHistorial,
                self.model.FechaHistorial,
                self.model.Linea,
                self.model.Interno,
                self.model.Dominio,
                self.model.FechaPatentado,
                self.model.KM,
                self.model.Asientos,
                self.model.TipoCombustible,
                self.model.Carroceria,
                self.model.ChasisCod,
                self.chasis_marca.ChasisMarca,
                self.chasis_modelo.ChasisModelo,
                self.model.ChasisAño,
                self.model.MotorCod,
                self.motor_marca.MotorMarca,
                self.motor_modelo.MotorModelo,
            )
            .join(
                self.chasis_modelo,
                self.chasis_modelo.IDChasisModelo == self.model.IDChasis,
            )
            .join(
                self.chasis_marca,
                self.chasis_modelo.IDChasisMarca == self.chasis_marca.IDChasisMarca,
            )
            .join(
                self.motor_modelo,
                self.motor_modelo.IDMotorModelo == self.model.IDMotor,
            )
            .join(
                self.motor_marca,
                self.motor_modelo.IDMotorMarca == self.motor_marca.IDMotorMarca,
            )
        )

    def _filtrar(
        self,
        stmt,
        fecha_desde,
        fecha_hasta,
        linea,
        interno,
        dominio,
        carroceria,
        chasis_marca,
        chasis_modelo,
        motor_marca,
        motor_modelo,
    ):
        if fecha_desde:
            stmt = stmt.where(self.model.FechaHistorial >= fecha_desde)

        if fecha_hasta:
            stmt = stmt.where(self.model.FechaHistorial <= fecha_hasta)

        if linea:
            stmt = stmt.where(self.model.Linea == linea)

        if interno:
            stmt = stmt.where(self.model.Interno == interno)

        if dominio:
            stmt = stmt.where(self.model.Dominio.ilike(f"%{dominio}%"))

        if carroceria:
            stmt = stmt.where(self.model.Carroceria == carroceria)

        if chasis_marca:
            stmt = stmt.where(self.chasis_marca.ChasisMarca == chasis_marca)

        if chasis_modelo:
            stmt = stmt.where(self.chasis_modelo.ChasisModelo == chasis_modelo)

        if motor_marca:
            stmt = stmt.where(self.motor_marca.MotorMarca == motor_marca)

        if motor_modelo:
            stmt = stmt.where(self.motor_modelo.MotorModelo == motor_modelo)

        return stmt

    def get_historial(
        self,
        db,
        fecha_desde,
        fecha_hasta,
        linea,
        interno,
        dominio,
        carroceria,
        chasis_marca,
        chasis_modelo,
        motor_marca,
        motor_modelo,
        limit,
        cursor_valor,
        cursor_id,
    ):
        stmt = self._filtrar(
            self._select_base(),
            fecha_desde,
            fecha_hasta,
            linea,
            interno,
            dominio,
            carroceria,
            chasis_marca,
            chasis_modelo,
            motor_marca,
            motor_modelo,
        )
        return self._paginar(
            db,
            stmt,
            limit,
            pk_col=("IDParqueMovilHistorial", self.model.IDParqueMovilHistorial),
            valor_col=("FechaHistorial", self.model.FechaHistorial),
            cursor=(cursor_id, cursor_valor),
        )

    def stmt_exportar(
        self,
        fecha_desde,
        fecha_hasta,
        linea,
        interno,
        dominio,
        carroceria,
        chasis_marca,
        chasis_modelo,
        motor_marca,
        motor_modelo,
    ):
        stmt = self._filtrar(
            self._select_base(),
            fecha_desde,
            fecha_hasta,
            linea,
            interno,
            dominio,
            carroceria,
            chasis_marca,
            chasis_modelo,
            motor_marca,
            motor_modelo,
        )
        return stmt.order_by(
            self.model.FechaHistorial.desc(),
            self.model.IDParqueMovilHistorial.asc(),
        )


class InternoVigenciaRepository(BaseRepository[InternoVigenciaModel]):
    model = InternoVigenciaModel
