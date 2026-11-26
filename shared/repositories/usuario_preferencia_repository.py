from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from shared.db.models import UsuarioPreferencia as UP


def obtener(db: Session, id_usuario: int, clave: str) -> dict[str, Any] | None:
    return db.scalar(
        select(UP.Valor).where(UP.IDUsuario == id_usuario, UP.Clave == clave)
    )


def guardar(db: Session, id_usuario: int, clave: str, valor: dict[str, Any]) -> None:
    stmt = insert(UP).values(IDUsuario=id_usuario, Clave=clave, Valor=valor)
    db.execute(
        stmt.on_conflict_do_update(
            index_elements=[UP.IDUsuario, UP.Clave],
            set_={"Valor": stmt.excluded.Valor, "Actualizado": func.now()},
        )
    )
    db.commit()


def borrar(db: Session, id_usuario: int, clave: str) -> None:
    db.execute(delete(UP).where(UP.IDUsuario == id_usuario, UP.Clave == clave))
    db.commit()
