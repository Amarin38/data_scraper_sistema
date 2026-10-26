from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DDLElement


class CreateMatView(DDLElement):
    def __init__(self, nombre, selectable):
        self.nombre = nombre
        self.selectable = selectable


@compiles(CreateMatView)
def _compile(element, compiler, **kw):
    sql = compiler.sql_compiler.process(element.selectable, literal_binds=True)
    return f"CREATE MATERIALIZED VIEW IF NOT EXISTS {element.nombre} AS {sql}"
