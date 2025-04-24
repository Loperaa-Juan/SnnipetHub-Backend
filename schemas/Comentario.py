import datetime as _dt
import uuid as _uuid
import pydantic as _pydantic

class _ComentarioBase(_pydantic.BaseModel):
    contenido: str


class ComentarioCreate(_ComentarioBase):
    Userid: _uuid.UUID
    Publicacionid: _uuid.UUID

    model_config = _pydantic.ConfigDict(from_attributes=True)


class Comentario(_ComentarioBase):
    ComentarioId: _uuid.UUID
    fecha_creacion: _dt.datetime
    activo: bool
    actualiza: _dt.datetime
    Userid: _uuid.UUID
    Publicacionid: _uuid.UUID

    model_config = _pydantic.ConfigDict(from_attributes=True)
