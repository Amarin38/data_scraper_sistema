from fastapi import APIRouter

from src.api.v1.endpoints import (
    estadisticas,
    existencia_stock,
    ficha_stock,
    generales,
    parque_movil,
    repuesto,
)

api_router = APIRouter()
api_router.include_router(ficha_stock.router)
api_router.include_router(existencia_stock.router)
api_router.include_router(parque_movil.router)
api_router.include_router(repuesto.router)
api_router.include_router(estadisticas.router)
api_router.include_router(generales.router)
