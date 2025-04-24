import datetime as _dt
import uuid as _uuid
import pydantic as _pydantic


class _SnippetBase(_pydantic.BaseModel):
    Titulo: str
    snippet: str


class SnippetCreate(_SnippetBase):
    Userid: _uuid.UUID
    Lenguaje: str

    model_config = _pydantic.ConfigDict(from_attributes=True)

class LeadCreate(_SnippetBase):
    pass

class Snippet(_SnippetBase):
    Snippetid: _uuid.UUID
    fecha_creacion: _dt.datetime
    activo: bool
    actualiza: _dt.datetime
    Userid: _uuid.UUID
    Lenguaje: str

    model_config = _pydantic.ConfigDict(from_attributes=True)
