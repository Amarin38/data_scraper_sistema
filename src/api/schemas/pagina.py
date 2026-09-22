from pydantic import BaseModel


class Pagina[T](BaseModel):
    items: list[T]
    next_cursor: int | None
