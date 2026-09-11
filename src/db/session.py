import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.constants import (
    DATABASE_URL_AIVEN,
    DATABASE_URL_POSTGRESQL,
)

dbbase = declarative_base()
logger = logging.getLogger(__name__)


def _crear_engine_postgresql():
    return create_engine(
        DATABASE_URL_POSTGRESQL,
        pool_size=5,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"connect_timeout": 5},
    )


def _crear_engine_aiven():
    return create_engine(
        DATABASE_URL_AIVEN,
        echo=False,
        pool_pre_ping=True,
        hide_parameters=True,
        pool_recycle=1800,
        insertmanyvalues_page_size=10000,
        connect_args={"connect_timeout": 5},
    )


def _verificar(engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception("Fallo la conexion a %s", engine.url.host)
        engine.dispose()
        return False


def _resolver_engine():
    for nombre, factory in (
        ("postgresql", _crear_engine_postgresql),
        ("aiven", _crear_engine_aiven),
    ):
        engine = factory()
        if _verificar(engine):
            return nombre, engine
    raise RuntimeError("Ninguna base de datos disponible")


nombre, engine = _resolver_engine()
SessionLocal = sessionmaker(bind=engine)
u = make_url(str(engine.url))

print(f"activa: {nombre}")
print("user:", u.username)
print("host:", u.host)
print("port:", u.port)
print("db:  ", u.database)
