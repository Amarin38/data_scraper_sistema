from fastapi import APIRouter, Depends

from src.api.v1.endpoints import (
    auth,
    estadisticas,
    existencia_stock,
    ficha_stock,
    generales,
    inicio,
    parque_movil,
    repuesto,
    salud,
)
from src.core.auth import usuario_actual

api_router = APIRouter()

protegido = [Depends(usuario_actual)]

api_router.include_router(inicio.router, dependencies=protegido)
api_router.include_router(ficha_stock.router, dependencies=protegido)
api_router.include_router(existencia_stock.router, dependencies=protegido)
api_router.include_router(parque_movil.router, dependencies=protegido)
api_router.include_router(repuesto.router, dependencies=protegido)
api_router.include_router(estadisticas.router, dependencies=protegido)
api_router.include_router(generales.router, dependencies=protegido)
api_router.include_router(auth.router)
api_router.include_router(salud.router)
