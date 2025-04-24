import base64
import fastapi.security as _security
from fastapi import HTTPException, Depends, File, UploadFile, Form

from jose import jwt, JWTError
from datetime import datetime, timedelta

import datetime as _dt
import sqlalchemy.orm as _orm
from passlib.context import CryptContext
import psycopg2

import database as _database
import models as _models

import schemas.user as _user
import schemas.Snippet as _snippet

from typing import Union, Optional
import os
from dotenv import load_dotenv

load_dotenv()

OAuth2_scheme = _security.OAuth2PasswordBearer("/token")

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")

# Crea el contexto para hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_username(username: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.username == username).first()

async def create_user(user: _user.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password= pwd_context.hash(user.hashed_password) 
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def create_snippet(
    user: _user.User,
    Titulo: str = Form(...),
    Lenguaje: str = Form(...),
    file: UploadFile = File(...),
    db: _orm.Session = Depends(get_db)
):
    
    file_content = file.file.read()

    # Crear un objeto Snippet
    snippet_obj = _models.Snippet(
        Titulo=Titulo,
        Userid=user.Userid,  
        Lenguaje=Lenguaje,
        snippet=file_content
    )

    db.add(snippet_obj)
    db.commit()
    db.refresh(snippet_obj)

    return snippet_obj

async def authenticate_user(username: str, password: str, db: _orm.Session):
    user = await get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={
            "WWW-Authenticate":"Bearer"
        })

    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={
            "WWW-Authenticate":"Bearer"
        })
    return user

def create_token(data: dict, time_expire: Union[datetime, None] = None):
    data_copy = data.copy()

    if time_expire is None:
        expires = datetime.utcnow() + timedelta(minutes=15)
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=JWT_SECRET, algorithm=ALGORITHM)
    
    return  token_jwt

async def get_current_user(db: _orm.Session = Depends(get_db), token: str = Depends(OAuth2_scheme)):
    try:
        token_decode = jwt.decode(token, key=JWT_SECRET, algorithms=[ALGORITHM])
        user_id = token_decode.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(_models.User).filter_by(Userid=user_id).first()  
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={
            "WWW-Authenticate": "Bearer"
        })

    return user

async def get_snippets_by_user(user: _user.User, db: _orm.Session = Depends(get_db)):
    return db.query(_models.Snippet).filter(_models.Snippet.Userid == user.Userid).all()

async def _Snippet_selector(Snippetid: str, user: _user.User, db: _orm.Session):
    Snippet = (
        db.query(_models.Snippet)
        .filter_by(Userid = user.Userid)
        .filter(_models.Snippet.Snippetid == Snippetid)
        .first()
    )

    if Snippet is None:
        raise HTTPException(status_code=404, detail="Snippet does not exist")

    return Snippet

async def update_snippet(Snippetid: str, Titulo: Optional[str], Lenguaje: Optional[str], file: Optional[UploadFile], user: _user.User, db: _orm.Session):
    snippet_db = await _Snippet_selector(Snippetid, user, db)

    if Titulo:
        snippet_db.Titulo = Titulo

    if Lenguaje:
        snippet_db.Lenguaje = Lenguaje

    if file:
        snippet_db.snippet = file.file.read()

    snippet_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(snippet_db)

    return snippet_db

async def delete_snippet(Snippetid: str, user: _user.User, db: _orm.Session):
    snippet_db = await _Snippet_selector(Snippetid, user, db)

    db.delete(snippet_db)
    db.commit()

    return {"detail": "Snippet deleted"}

async def create_comment(Publicacionid: str, user: _user.User, db: _orm.Session, comment: str):

    comment_obj = _models.Comentario(
        contenido=comment,
        Userid=user.Userid,
        Publicacionid=Publicacionid  
    )

    db.add(comment_obj)
    db.commit()
    db.refresh(comment_obj)

    return comment_obj

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

async def get_comments_by_me(user: _user.User, db: _orm.Session):
    comments = db.query(_models.Comentario).filter(_models.Comentario.Userid == user.Userid).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments

async def get_comments_by_user(Userid: str, db: _orm.Session):
    comments = db.query(_models.Comentario).filter(_models.Comentario.Userid == Userid).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments

def get_comments_by_publicacion(Publicacionid: str, db: _orm.Session):
    comments = db.query(_models.Comentario).filter(_models.Comentario.Publicacionid == Publicacionid).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments

def update_comment(ComentarioId: str, Contenido: str, user: _user.User, db: _orm.Session):
    comment_db = db.query(_models.Comentario).filter(_models.Comentario.ComentarioId == ComentarioId).first()

    if comment_db is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if user.Userid != comment_db.Userid:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this comment")


    comment_db.contenido = Contenido

    db.commit()
    db.refresh(comment_db)

    return comment_db

def delete_comment(ComentarioId: str, user: _user.User, db: _orm.Session):
    comment_db = db.query(_models.Comentario).filter(_models.Comentario.ComentarioId == ComentarioId).first()

    if comment_db is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if user.Userid != comment_db.Userid:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this comment")

    db.delete(comment_db)
    db.commit()

    return {"detail": "Comment deleted"}