from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.constants import DATABASE_URL, DB_CA

dbbase = declarative_base()
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    hide_parameters=True,
    connect_args={"ssl": {"ca": str(DB_CA)}},
    insertmanyvalues_page_size=10000,
)
SessionLocal = sessionmaker(bind=engine)


u = make_url(DATABASE_URL)
print("user:", u.username)
print("host:", u.host)
print("port:", u.port)
print("db:  ", u.database)
