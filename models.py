import datetime as _dt
from uuid import uuid4 as _uuid
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.context import CryptContext

import database as _database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(_database.Base):
    __tablename__ = "user"
    Userid = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    username = _sql.Column(_sql.String, index=True, unique=True)
    full_name = _sql.Column(_sql.String, index=True)
    email = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True)
    actualiza = _sql.Column(_sql.DateTime, nullable=True, default=_dt.datetime.utcnow)

    publicaciones = _orm.relationship("Publicacion", back_populates="user")
    snippets = _orm.relationship("Snippet", back_populates="user")
    comentarios = _orm.relationship("Comentario", back_populates="user")

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class Publicacion(_database.Base):
    __tablename__ = "publicacion"
    Publicacionid = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    Userid = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("user.Userid"))
    SnippetId = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("snippet.Snippetid"))
    titulo = _sql.Column(_sql.String, index=True)
    contenido = _sql.Column(_sql.Text, index=True)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True)
    actualiza = _sql.Column(_sql.DateTime, nullable=True, default=_dt.datetime.utcnow)

    user = _orm.relationship("User", back_populates="publicaciones")
    Snippet = _orm.relationship("Snippet", back_populates="publicaciones")
    comentarios = _orm.relationship("Comentario", back_populates="publicacion")


class Snippet(_database.Base):
    __tablename__ = "snippet"
    Snippetid = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    Titulo = _sql.Column(_sql.String, index=True)
    Userid = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("user.Userid"))
    Lenguaje = _sql.Column(_sql.String, nullable=False, index=True)
    snippet = _sql.Column(_sql.LargeBinary, index=True)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True)
    actualiza = _sql.Column(_sql.DateTime, nullable=True, default=_dt.datetime.utcnow)

    user = _orm.relationship("User", back_populates="snippets")
    publicaciones = _orm.relationship("Publicacion", back_populates="Snippet")

class Comentario(_database.Base):
    __tablename__ = "comentario"
    ComentarioId = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    contenido = _sql.Column(_sql.Text, index=True)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    Userid = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("user.Userid"))
    Publicacionid = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("publicacion.Publicacionid"))
    activo = _sql.Column(_sql.Boolean, default=True)
    actualiza = _sql.Column(_sql.DateTime, nullable=True, default=_dt.datetime.utcnow)

    publicacion = _orm.relationship("Publicacion", back_populates="comentarios")
    user = _orm.relationship("User", back_populates="comentarios")
