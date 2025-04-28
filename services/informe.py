# services/informe.py

from services.database import get_db
from models import User, Snippet, Publicacion, Comentario
import sqlalchemy.orm as _orm
from sqlalchemy import select, func 
import schemas.user as _user

def generar_informe(db: _orm.Session, user: _user.User):

    cantidad_usuarios = db.query(func.count(User.Userid)).scalar()
    cantidad_snippets = db.query(func.count(Snippet.Snippetid)).scalar()
    cantidad_publicaciones = db.query(func.count(Publicacion.Publicacionid)).scalar()
    cantidad_comentarios = db.query(func.count(Comentario.ComentarioId)).scalar()
    cantidad_usuarios_activos = db.query(func.count(User.Userid)).filter(User.activo == True).scalar()
    cantidad_snippets_aprobados = db.query(func.count(Snippet.Snippetid)).filter(Snippet.activo == True).scalar()
    # cantidad_publicaciones_recientes = db.query(func.count(Publicacion.Publicacionid)).filter(Publicacion.fecha_creacion >= func.now() - func.interval('30 days')).scalar()


    return {
        "total_usuarios": cantidad_usuarios,
        "total_snippets": cantidad_snippets,
        "total_publicaciones": cantidad_publicaciones,
        "total_comentarios": cantidad_comentarios,
        "snippets_aprobados": cantidad_snippets_aprobados,
        "usuarios_activos": cantidad_usuarios_activos,
        # "publicaciones_recientes": cantidad_publicaciones_recientes,
    }
