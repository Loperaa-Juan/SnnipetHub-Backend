import models as _models
import schemas.user as _user

import sqlalchemy.orm as _orm
from fastapi import HTTPException

async def create_comment(Publicacionid: str , user: _user.User, db: _orm.Session, comment: str):

    # Verificar si la publicación existe
    publicacion = db.query(_models.Publicacion).filter(_models.Publicacion.Publicacionid == Publicacionid).first()
    if publicacion is None:
        raise HTTPException(status_code=404, detail="Publication not found")

    comment_obj = _models.Comentario(
        contenido=comment,
        Userid=user.Userid,
        Publicacionid=Publicacionid  
    )

    db.add(comment_obj)
    db.commit()
    db.refresh(comment_obj)

    return comment_obj

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
    results = (
        db.query(_models.Comentario.contenido, _models.User.username)
        .join(_models.User, _models.User.Userid == _models.Comentario.Userid)
        .filter(_models.Comentario.Publicacionid == Publicacionid)
        .all()
    )
    
    if not results:
        raise HTTPException(status_code=404, detail="No comments found")
    
    return [
        {"comentario": contenido, "usuario": username}
        for contenido, username in results
    ]

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