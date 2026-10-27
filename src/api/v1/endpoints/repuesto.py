from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.repuesto_schema import (
    RepuestoOffsetOut,
    RepuestoOut,
)
from src.api.utils import Limite
from src.core.enums import FormatoEnum
from src.core.exports import exportacion, iterar_filas, limpiar_nombre
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.repuesto_repository import RepuestoRepository

router = APIRouter(prefix="/repuestos", tags=["repuestos"])
repo = RepuestoRepository()

COLUMNAS_EXPORT = [c for c in RepuestoOut.model_fields if c != "IDRepuesto"]


@router.get(
    "",
    response_model=RepuestoOffsetOut,
    status_code=200,
    summary="Lista todos los repuestos.",
)
def listar(
    db: DB,
    conjunto: str | None = None,
    descripcion: str | None = None,
    codigo: str | None = None,
    critico: bool = False,
    limit: Limite = 50,
    page: int = 0,
):
    return repo.get_repuestos(db, conjunto, descripcion, codigo, critico, limit, page)


@router.get(
    "/conjuntos",
    response_model=list[str],
    status_code=200,
    summary="Devuelve todos los conjuntos de los repuestos.",
)
def get_conjuntos(db: DB):
    return repo.get_distinct_by_col(db, RepuestoModel.Conjunto)


@router.get("/exportar")
def exportar_repuestos(
    formato: FormatoEnum = FormatoEnum.CSV,
    nombre: str | None = None,
    validar: bool | None = False,
    conjunto: str | None = None,
    descripcion: str | None = None,
    codigo: str | None = None,
    critico: bool | None = None,
):
    stmt = repo.stmt_exportar(
        conjunto=conjunto,
        descripcion=descripcion,
        codigo=codigo,
        critico=critico,
    )

    def transformar(f):
        f = dict(f)
        if formato != FormatoEnum.JSON:
            f["Critico"] = "Si" if f["Critico"] else "No"
        return f

    return exportacion(
        stmt,
        COLUMNAS_EXPORT,
        formato,
        limpiar_nombre(nombre) or "repuestos",
        transformar=transformar,
        validar=validar,
    )
