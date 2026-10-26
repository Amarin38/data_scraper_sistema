from sqlalchemy import column, select, table

from src.db.models.parque_movil_historial_model import ParqueMovilHistorialModel as pmh
from src.db.views._ddl import CreateMatView

NOMBRE = "carrocerias"

SELECT = select(pmh.Carroceria).where(pmh.Carroceria.is_not(None)).distinct()

CREAR = [
    CreateMatView(NOMBRE, SELECT),
    f'CREATE UNIQUE INDEX IF NOT EXISTS ux_{NOMBRE} ON {NOMBRE} ("Carroceria")',
]

t = table(NOMBRE, column("Carroceria"))
