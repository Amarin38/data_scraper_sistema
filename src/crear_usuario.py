import getpass
import sys

from sqlalchemy import select

from src.core.enums import TipoUsuarioLoginEnum
from src.core.security import hashear
from src.db.models.usuario_model import UsuarioModel
from src.db.session import SessionLocal


def main() -> None:
    usuario = input("Usuario: ").strip().lower()
    tipo = input("Tipo (Admin/User) [User]: ").strip() or "User"
    password = getpass.getpass("Contraseña: ")

    if getpass.getpass("Repetir: ") != password:
        sys.exit("Las contraseñas no coinciden")

    with SessionLocal() as s:
        if s.scalar(select(UsuarioModel).where(UsuarioModel.User == usuario)):
            sys.exit("Ese usuario ya existe")
        s.add(
            UsuarioModel(
                User=usuario,
                PasswordHash=hashear(password),
                TipoUser=TipoUsuarioLoginEnum(tipo),
            )
        )
        s.commit()
    print(f"Usuario '{usuario}' creado ({tipo})")


if __name__ == "__main__":
    main()
