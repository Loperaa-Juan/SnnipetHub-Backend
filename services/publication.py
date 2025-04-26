import sqlalchemy.orm as _orm
from fastapi import HTTPException

import base64
from typing import Optional

import models as _models
import schemas.user as _user

async def create_publicacion(Titulo: str, Contenido: str, SnippetId: str, user: _user.User, db: _orm.Session):
    publicacion_obj = _models.Publicacion(
        titulo=Titulo,
        contenido=Contenido,
        SnippetId=SnippetId,
        Userid=user.Userid  
    )

    db.add(publicacion_obj)
    db.commit()
    db.refresh(publicacion_obj)

    return publicacion_obj

async def get_publicaciones_by_user(user: _user.User, db: _orm.Session):
    
    publicaciones = db.query(_models.Publicacion).filter(_models.Publicacion.Userid == user.Userid).all()
    if not publicaciones:
        raise HTTPException(status_code=404, detail="No publications found")
    resultado = []
    for publicacion in publicaciones:
        archivo = archivo = db.query(_models.Snippet).get(publicacion.SnippetId)
        if not archivo:
            raise HTTPException(status_code=404, detail="Snippet not found")
        resultado.append({
            "id": publicacion.Publicacionid,
            "titulo": publicacion.titulo,
            "contenido": publicacion.contenido,
            "archivo": base64.b64encode(archivo.snippet).decode("utf-8")
        })
    return resultado

async def get_publicacion_by_id(Publicacionid: str, db: _orm.Session):
    publicacion = db.query(_models.Publicacion).filter(_models.Publicacion.Publicacionid == Publicacionid).first()
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    archivo = db.query(_models.Snippet).get(publicacion.SnippetId)
    if not archivo:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "id": publicacion.Publicacionid,
        "titulo": publicacion.titulo,
        "contenido": publicacion.contenido,
        "archivo": base64.b64encode(archivo.snippet).decode("utf-8")
    }

async def update_publicacion(Publicacionid: str, Titulo: Optional[str], user:_user.User, Snippetid: str ,Contenido: Optional[str], db: _orm.Session):
    publicacion_db = db.query(_models.Publicacion).filter(_models.Publicacion.Publicacionid == Publicacionid).first()

    if user.Userid != publicacion_db.Userid:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this publication")

    if not publicacion_db:
        raise HTTPException(status_code=404, detail="Publication not found")

    if Titulo:
        publicacion_db.titulo = Titulo

    if Contenido:
        publicacion_db.contenido = Contenido

    if Snippetid:
        publicacion_db.SnippetId = Snippetid

    db.commit()
    db.refresh(publicacion_db)

    return publicacion_db

async def delete_publicacion(Publicacionid: str, user: _user.User, db: _orm.Session):
    publicacion_db = db.query(_models.Publicacion).filter(_models.Publicacion.Publicacionid == Publicacionid).first()

    if user.Userid != publicacion_db.Userid:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this publication")

    if not publicacion_db:
        raise HTTPException(status_code=404, detail="Publication not found")

    db.delete(publicacion_db)
    db.commit()

    return {"detail": "Publication deleted"}