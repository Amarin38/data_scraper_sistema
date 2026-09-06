from fastapi import APIRouter

from src.api.v1.endpoints import existencia_stock, ficha_stock, repuesto

api_router = APIRouter()
api_router.include_router(ficha_stock.router)
api_router.include_router(existencia_stock.router)
api_router.include_router(repuesto.router)
