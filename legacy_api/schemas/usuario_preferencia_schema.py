from typing import Any

from pydantic import BaseModel, Field


class PanelConfig(BaseModel):
    Visible: bool = True
    Ancho: int | None = Field(None, ge=2, le=8)  # None = automático
    Bloque: int | None = Field(None, ge=0, le=2)  # None = automático
    Orden: int | None = Field(None, ge=0, le=100)  # None = automático


class TableroIn(BaseModel):
    v: int = 1
    Paneles: dict[str, PanelConfig] = Field(max_length=30)


class TableroOut(BaseModel):
    v: int
    Paneles: dict[str, dict[str, Any]]
    Permitidos: list[str]
