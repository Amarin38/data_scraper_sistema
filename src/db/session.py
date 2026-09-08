from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.constants import (
    DATABASE_URL_AIVEN,
    DATABASE_URL_POSTGRESQL,
    DB_CA_AIVEN,
)

dbbase = declarative_base()

engine_aiven = create_engine(
    DATABASE_URL_AIVEN,
    echo=False,
    pool_pre_ping=True,
    hide_parameters=True,
    connect_args={"ssl": {"ca": str(DB_CA_AIVEN)}},
    insertmanyvalues_page_size=10000,
)

engine_postgresql = create_engine(
    DATABASE_URL_POSTGRESQL,
    pool_size=5,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine_postgresql)


u = make_url(DATABASE_URL_POSTGRESQL)
print("user:", u.username)
print("host:", u.host)
print("port:", u.port)
print("db:  ", u.database)
