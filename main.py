from typing import List, Optional

from fastapi import FastAPI, Depends, Form, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

import sqlalchemy.orm as _orm
from datetime import timedelta

import schemas.user as _user
import schemas.Snippet as _snippet
import schemas.Comentario as _comentario

import services.user as _userServices
import services.database as _databaseServices
import services.snippet as _snippetServices
import services.publication as _publicationServices
import services.comments as _commentsServices

import services.informe as _informeServices

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users/me", response_model=_user.User)
async def get_user(user: _user.User = Depends(_userServices.get_current_user)):
    return user


@app.get("/users/{username}", response_model=_user.User)
async def get_user_by_id(
    username: str, db: _orm.Session = Depends(_databaseServices.get_db)
):
    user = await _userServices.get_user_by_username(username=username, db = db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: _orm.Session = Depends(_databaseServices.get_db),):
    user = await _userServices.authenticate_user(form_data.username, form_data.password, db)

    access_token_expires = timedelta(minutes=30)
    access_token_jwt = _userServices.create_token({"sub": user.username, "id": str(user.Userid), "role": str(user.role)}, access_token_expires)

    return {
        "access_token": access_token_jwt,
        "token_type": "bearer"
    }


@app.post("/users")
async def create_user(
    user: _user.UserCreate, db: _orm.Session = Depends(_databaseServices.get_db)
):
    db_user = await _userServices.get_user_by_username(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user = await _userServices.create_user(user, db)

    return user

@app.get("/top_users")
async def top_users(
    db: _orm.Session = Depends(_databaseServices.get_db),
    user: _user.User = Depends(_userServices.get_current_user)
):
    top = await _userServices.top_five_users(db=db, user=user)

    return top
    

# CRUD ENDPOINTS - Snippets
@app.post("/create/snippets", tags=["snippets"])
def create_snippet(
    Titulo: str = Form(...),
    Lenguaje: str = Form(...),
    descripcion: str = Form(...),
    user: _user.User = Depends(_userServices.get_current_user),
    file: UploadFile = File(...), 
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return  _snippetServices.create_snippet(Titulo=Titulo, Lenguaje=Lenguaje, descripcion=descripcion, user=user, db=db, file=file)

@app.get("/snippets/me",tags=["snippets"], response_model=List[_snippet.Snippet])
async def get_snippets(user: _user.User = Depends(_userServices.get_current_user), db: _orm.Session = Depends(_databaseServices.get_db)):
    snippets = await _snippetServices.get_snippets_by_user(user=user, db=db)
    return snippets

@app.put("/snippets/{snippet_id}", tags=["snippets"])
async def update_snippet(
    snippet_id: str,
    Titulo: Optional[str] = Form(None),
    Lenguaje: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    snippet = await _snippetServices.update_snippet(snippet_id, Titulo, Lenguaje,descripcion, file, user, db=db)
    return snippet

@app.get("/snippets/{username}", tags=["snippets"])
async def get_snippets_by_user(
    username: str,
    db: _orm.Session = Depends(_databaseServices.get_db),
    user: _user.User = Depends(_userServices.get_current_user),
):
    snippets = await _snippetServices.get_snippets_by_username(username=username, db=db, user=user)
    if not snippets:
        raise HTTPException(status_code=404, detail="Snippets not found")
    return snippets


@app.delete("/snippets/{snippet_id}", tags=["snippets"])
async def delete_snippet(
    snippet_id: str,
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    snippet = await _snippetServices.delete_snippet(snippet_id, user, db=db)
    return snippet


# CRUD ENDPOINTS - Publicaciones
@app.post("/publicaciones", tags=["publicaciones"])
async def create_publicacion(
    Titulo: str = Form(...),
    Contenido: str = Form(...),
    SnippetId: str = Form(...),
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _publicationServices.create_publicacion(Titulo=Titulo, Contenido=Contenido, SnippetId=SnippetId, user=user, db=db)

@app.get("/publicaciones/me", tags=["publicaciones"])
async def get_publicaciones(
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _publicationServices.get_publicaciones_by_user(user, db)

@app.get("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def get_publicacion_by_id(
    publicacion_id: str,
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _publicationServices.get_publicacion_by_id(publicacion_id, db)

@app.get("/publications/user/{username}", tags=["publicaciones"])
async def get_publicaciones(
    username: str,
    db: _orm.Session = Depends(_databaseServices.get_db),
    user: _user.User = Depends(_userServices.get_current_user),
):
    return await _publicationServices.get_publication_by_user(username=username, db=db, user=user)

@app.put("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def update_publicacion(
    publicacion_id: str,
    Titulo: Optional[str] = Form(None),
    Contenido: Optional[str] = Form(None),
    SnippetId: Optional[str] = Form(None),
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _publicationServices.update_publicacion(Publicacionid=publicacion_id, Titulo=Titulo, Contenido=Contenido, Snippetid=SnippetId, user=user, db=db)

@app.delete("/publicaciones/{publicacion_id}", tags=["publicaciones"])
async def delete_publicacion(
    publicacion_id: str,
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _publicationServices.delete_publicacion(Publicacionid=publicacion_id, user=user, db=db)

# CRUD ENDPOINTS - Comentarios
@app.post("/create/comentario", tags=["comments"])
async def create_comment(
    comentario: str = Form(...),
    Publicacionid: str = Form(...),
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _commentsServices.create_comment(Publicacionid=Publicacionid, comment=comentario, user=user, db=db)

@app.get("/comentarios/user/me", tags=["comments"])
async def get_comments_me(
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _commentsServices.get_comments_by_me(user, db)

@app.get("/comentarios/user/{Userid}", tags=["comments"])
async def get_comments_user(
    Userid: str,
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return await _commentsServices.get_comments_by_user(Userid=Userid, db=db)

@app.get("/comentarios/{Publicacionid}", tags=["comments"])
def get_comments_public(
    Publicacionid: str,
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return _commentsServices.get_comments_by_publicacion(Publicacionid=Publicacionid, db=db)

@app.put("/comentarios/{ComentarioId}", tags=["comments"])
def update_comment(
    ComentarioId: str,
    Contenido: Optional[str] = Form(None),
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return  _commentsServices.update_comment(ComentarioId=ComentarioId, Contenido=Contenido, user=user, db=db)

@app.delete("/comentarios/{ComentarioId}", tags=["comments"])
def delete_comment(
    ComentarioId: str,
    user: _user.User = Depends(_userServices.get_current_user),
    db: _orm.Session = Depends(_databaseServices.get_db)
):
    return _commentsServices.delete_comment(ComentarioId=ComentarioId, user=user, db=db)

@app.get("/admin/informe")
def obtener_informe(user: _user.User = Depends(_userServices.get_current_user), db: _orm.Session = Depends(_databaseServices.get_db)):
    informe = _informeServices.generar_informe(user=user, db=db)
    return informe