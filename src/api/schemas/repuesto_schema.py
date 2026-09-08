from pydantic import BaseModel


class RepuestoBase(BaseModel):
    IDRepuesto: int
    Familia: str
    Articulo: str
    Descripcion: str


class RepuestoCreate(RepuestoBase):
    pass


class RepuestoOut(RepuestoBase):
    IDRepuesto: int
    Familia: str
    Articulo: str
    Descripcion: str

    model_config = {"from_attributes": True}
