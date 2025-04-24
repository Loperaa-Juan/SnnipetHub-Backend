import uuid as _uuid
import datetime as _dt
import pydantic as _pydantic


class _PublicacionBase(_pydantic.BaseModel):
    titulo: str
    contenido: str


class PublicacionCreate(_PublicacionBase):
    Userid: _uuid.UUID
    SnippetId: _uuid.UUID

    model_config = _pydantic.ConfigDict(from_attributes=True)


class Publicacion(_PublicacionBase):
    Publicacionid: _uuid.UUID
    fecha_creacion: _dt.datetime
    activo: bool
    actualiza: _dt.datetime
    Userid: _uuid.UUID
    SnippetId: _uuid.UUID

    model_config = _pydantic.ConfigDict(from_attributes=True)
