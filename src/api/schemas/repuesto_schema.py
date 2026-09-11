from pydantic import BaseModel, ConfigDict, Field


class RepuestoCreate(BaseModel):
    Familia: str = Field(max_length=3)
    Articulo: str = Field(max_length=5)
    Descripcion: str | None = None


class RepuestoPatch(BaseModel):
    Descripcion: str


class RepuestoOut(BaseModel):
    IDRepuesto: int
    Familia: str
    Articulo: str
    Descripcion: str | None

    model_config = ConfigDict(from_attributes=True)
