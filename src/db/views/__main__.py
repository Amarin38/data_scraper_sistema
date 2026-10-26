import sys

from src.db.session import SessionLocal
from src.db.views import crear_vistas, refrescar_vistas

accion = sys.argv[1] if len(sys.argv) > 1 else "crear"

with SessionLocal() as db:
    if accion == "crear":
        crear_vistas(db)
    elif accion == "refrescar":
        refrescar_vistas(db)
    else:
        sys.exit(f"Acción desconocida: {accion} (usá 'crear' o 'refrescar')")
