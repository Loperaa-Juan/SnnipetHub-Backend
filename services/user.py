from datetime import datetime, timedelta
from typing import Union
import os

from jose import jwt, JWTError
from dotenv import load_dotenv
from passlib.context import CryptContext

import fastapi.security as _security
from fastapi import HTTPException, Depends

import models as _models
import schemas.user as _user
from services.database import get_db

import sqlalchemy.orm as _orm
from sqlalchemy import func, desc

# Crea el contexto para hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

OAuth2_scheme = _security.OAuth2PasswordBearer("/token")

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")

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

async def top_five_users( user: _user.User, db: _orm.Session = Depends(get_db),):
    top_five = db.query(
        _models.User.Userid,
        _models.User.username,
        _models.User.full_name,
        func.count( _models.Publicacion.Userid )
    ).join(
        _models.Publicacion,
        _models.User.Userid == _models.Publicacion.Userid
    ).group_by(
        _models.User.Userid,
        _models.User.username,
        _models.User.full_name,
    ).order_by(
        desc( func.count( _models.Publicacion.Userid ) )
    ).limit( 6 )

    top_five = [
        {
            "id": r[0],
            "username": r[1],
            "full_name": r[2],
            "numero_publicaciones": r[3]
        } for r in top_five
    ]
    return top_five