import logging
import time

from sqlalchemy import text

from src.db.session import engine
from src.db.views import (
    carrocerias,
    consumo_mensual,
    consumo_mensual_deposito,
    gasto_mensual,
)

logger = logging.getLogger(__name__)

# Si una vista depende de otra, va después de la que usa.
VISTAS = [
    carrocerias,
    consumo_mensual,
    consumo_mensual_deposito,
    gasto_mensual,
]
TABLAS_MANTENIMIENTO = ["parque_movil_historial", "duracion_repuestos"]


def crear_vistas(db):
    for v in VISTAS:
        for paso in v.CREAR:
            db.execute(text(paso) if isinstance(paso, str) else paso)
    db.commit()


def refrescar_vistas(db, concurrente: bool = False, work_mem: str = "256MB"):
    """Refresca cada vista en su propia transacción.

    concurrente=False: reconstruye la vista (más rápido, bloquea lecturas de esa vista).
    concurrente=True: compara contra la vieja (más lento, no bloquea lecturas).
    work_mem y jit se aplican solo a esta sesión (SET LOCAL).
    """
    modo = "CONCURRENTLY " if concurrente else ""
    for v in VISTAS:
        t0 = time.perf_counter()
        db.execute(text(f"SET LOCAL work_mem = '{work_mem}'"))
        db.execute(text("SET LOCAL max_parallel_workers_per_gather = 0"))
        db.execute(text("SET LOCAL jit = off"))
        db.execute(text(f"REFRESH MATERIALIZED VIEW {modo}{v.NOMBRE}"))
        db.commit()
        logger.info("view  %s refrescada en %.0fs", v.NOMBRE, time.perf_counter() - t0)


def mantenimiento():
    """VACUUM ANALYZE fuera de transacción, para que el planner conserve estadísticas al día."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for tabla in TABLAS_MANTENIMIENTO:
            conn.execute(text(f'VACUUM ANALYZE "{tabla}"'))
