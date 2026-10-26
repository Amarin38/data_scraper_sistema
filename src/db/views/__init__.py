from sqlalchemy import text

from src.db.views import carrocerias, consumo_mensual

# Si una vista depende de otra, va después de la que usa.
VISTAS = [carrocerias, consumo_mensual]


def crear_vistas(db):
    for v in VISTAS:
        for paso in v.CREAR:
            db.execute(text(paso) if isinstance(paso, str) else paso)
    db.commit()


def refrescar_vistas(db):
    for v in VISTAS:
        db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {v.NOMBRE}"))
    db.commit()
