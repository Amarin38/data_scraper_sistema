from pydantic import BaseModel, ConfigDict, Field


class RepuestoCreate(BaseModel):
    Familia: str = Field(max_length=3)
    Articulo: str = Field(max_length=5)
    Descripcion: str | None = None


class RepuestoPatch(BaseModel):
    Descripcion: str


class RepuestoOut(BaseModel):
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    Conjunto: str | None
    Condicion: str
    Critico: bool

    model_config = ConfigDict(from_attributes=True)


class RepuestoPaginadoOut(BaseModel):
    items: list[RepuestoOut]
    next_cursor: dict | None
