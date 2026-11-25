import logging
import sys

from src.db.session import SessionLocal
from src.db.views import crear_vistas, mantenimiento, refrescar_vistas

logging.basicConfig(level="INFO", format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

accion = sys.argv[1] if len(sys.argv) > 1 else "crear"

with SessionLocal() as db:
    if accion == "crear":
        crear_vistas(db)
    elif accion == "refrescar":
        refrescar_vistas(db, concurrente="concurrente" in sys.argv[2:])
    elif accion == "mantenimiento":
        mantenimiento()
    else:
        sys.exit(
            f"Acción desconocida: {accion} (usá 'crear', 'refrescar' o 'mantenimiento')"
        )
