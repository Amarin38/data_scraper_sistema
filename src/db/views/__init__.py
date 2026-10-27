from sqlalchemy import text

from src.db.session import engine
from src.db.views import carrocerias, consumo_mensual

# Si una vista depende de otra, va después de la que usa.
VISTAS = [carrocerias, consumo_mensual]
TABLAS_MANTENIMIENTO = ["parque_movil_historial", "duracion_repuestos"]


def crear_vistas(db):
    for v in VISTAS:
        for paso in v.CREAR:
            db.execute(text(paso) if isinstance(paso, str) else paso)
    db.commit()


def refrescar_vistas(db):
    for v in VISTAS:
        db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {v.NOMBRE}"))
    db.commit()


def mantenimiento():
    """VACUUM ANALYZE fuera de transacción, para que el planner conserve estadísticas al día."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for tabla in TABLAS_MANTENIMIENTO:
            conn.execute(text(f'VACUUM ANALYZE "{tabla}"'))
