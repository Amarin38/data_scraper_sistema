from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_router

app = FastAPI(title="API Estadisticas DOTA")
app.include_router(api_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.68.50:5173",
        "http://100.72.116.128:5173",
        "http://100.72.116.128:4173",
        "http://192.168.68.50:4173",
    ],
    allow_methods=["GET", "PUT", "POST"],
    allow_headers=["*"],
)
