from typing import List, Optional
from fastapi import FastAPI, Depends, Form, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

import sqlalchemy.orm as _orm
from datetime import timedelta

import schemas.user as _user
import schemas.Snippet as _snippet
import schemas.Comentario as _comentario

import services as _services

app = FastAPI()

@app.get("/users/me", response_model=_user.User)
async def get_user(user: _user.User = Depends(_services.get_current_user)):
    return user


@app.get("/users/{username}", response_model=_user.User)
async def get_user_by_id(
    username: str, db: _orm.Session = Depends(_services.get_db)
):
    user = await _services.get_user_by_username(username=username, db = db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: _orm.Session = Depends(_services.get_db),):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    access_token_expires = timedelta(minutes=30)
    access_token_jwt = _services.create_token({"sub": user.username, "id": str(user.Userid)}, access_token_expires)

    return {
        "access_token": access_token_jwt,
        "token_type": "bearer"
    }

@app.post("/users")
async def create_user(
    user: _user.UserCreate, db: _orm.Session = Depends(_services.get_db)
):
    db_user = await _services.get_user_by_username(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user = await _services.create_user(user, db)

    return user

# CRUD ENDPOINTS - Snippets
@app.post("/snippets", tags=["snippets"])
def create_snippet(
    Titulo: str,
    Lenguaje: str,
    user: _user.User = Depends(_services.get_current_user),
    file: UploadFile = File(...), 
    db: _orm.Session = Depends(_services.get_db)
):
    return  _services.create_snippet(Titulo=Titulo, Lenguaje=Lenguaje, user=user, db=db, file=file)

@app.get("/snippets/me",tags=["snippets"], response_model=List[_snippet.Snippet])
async def get_snippets(user: _user.User = Depends(_services.get_current_user), db: _orm.Session = Depends(_services.get_db)):
    snippets = await _services.get_snippets_by_user(user, db)
    return snippets

@app.put("/snippets/{snippet_id}", tags=["snippets"])
async def update_snippet(
    snippet_id: str,
    Titulo: Optional[str] = Form(None),
    Lenguaje: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    snippet = await _services.update_snippet(snippet_id, Titulo, Lenguaje, file, user, db=db)
    return snippet

@app.delete("/snippets/{snippet_id}", tags=["snippets"])
async def delete_snippet(
    snippet_id: str,
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    snippet = await _services.delete_snippet(snippet_id, user, db=db)
    return snippet

# CRUD ENDPOINTS - Publicaciones
@app.post("/publicaciones", tags=["publicaciones"])
async def create_publicacion(
    Titulo: str,
    Contenido: str,
    SnippetId: str,
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.create_publicacion(Titulo=Titulo, Contenido=Contenido, SnippetId=SnippetId, user=user, db=db)

@app.get("/publicaciones/me", tags=["publicaciones"])
async def get_publicaciones(
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.get_publicaciones_by_user(user, db)

@app.get("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def get_publicacion_by_id(
    publicacion_id: str,
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.get_publicacion_by_id(publicacion_id, db)

@app.put("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def update_publicacion(
    publicacion_id: str,
    Titulo: Optional[str] = Form(None),
    Contenido: Optional[str] = Form(None),
    SnippetId: Optional[str] = Form(None),
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.update_publicacion(Publicacionid=publicacion_id, Titulo=Titulo, Contenido=Contenido, Snippetid=SnippetId, user=user, db=db)

@app.delete("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def delete_publicacion(
    publicacion_id: str,
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.delete_publicacion(Publicacionid=publicacion_id, user=user, db=db)

# CRUD ENDPOINTS - Comentarios
@app.post("/comentarios", tags=["comments"])
async def create_comment(
    Publicacionid: str,
    Contenido: str,
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.create_comment(Publicacionid=Publicacionid, comment=Contenido, user=user, db=db)

@app.get("/comentarios/user/me", tags=["comments"])
async def get_comments_me(
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.get_comments_by_me(user, db)

@app.get("/comentarios/user/{Userid}", tags=["comments"])
async def get_comments_user(
    Userid: str,
    db: _orm.Session = Depends(_services.get_db)
):
    return await _services.get_comments_by_user(Userid=Userid, db=db)

@app.get("/comentarios/{Publicacionid}", tags=["comments"])
def get_comments_public(
    Publicacionid: str,
    db: _orm.Session = Depends(_services.get_db)
):
    return _services.get_comments_by_publicacion(Publicacionid=Publicacionid, db=db)

@app.put("/comentarios/{ComentarioId}", tags=["comments"])
def update_comment(
    ComentarioId: str,
    Contenido: Optional[str] = Form(None),
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return  _services.update_comment(ComentarioId=ComentarioId, Contenido=Contenido, user=user, db=db)

@app.delete("/comentarios/{ComentarioId}", tags=["comments"])
def delete_comment(
    ComentarioId: str,
    user: _user.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    return _services.delete_comment(ComentarioId=ComentarioId, user=user, db=db)