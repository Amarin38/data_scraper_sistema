from typing import Annotated

from fastapi import HTTPException, Query

Limite = Annotated[int, Query(ge=1, le=1000, description="Filas por página")]
Cursor = Annotated[
    int, Query(ge=0, description="IDFichaStock de la última fila anterior")
]

no_existe_existencia = HTTPException(404, "La existencia no existe.")
no_existe_repuesto = HTTPException(404, "El repuesto no existe.")

ya_existe_repuesto = HTTPException(405, "El repuesto ya existe.")
