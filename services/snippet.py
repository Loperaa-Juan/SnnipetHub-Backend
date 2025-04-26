import sqlalchemy.orm as _orm
from fastapi import File, Form, HTTPException
import base64
from typing import Optional, List
from fastapi import UploadFile, Depends
import datetime as _dt
import schemas.user as _user
import models as _models
from services.database import get_db

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