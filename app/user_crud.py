from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from fastapi import Response, status, Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

import models
import schemas
from exceptions import credential_exception
from keys import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_user(usr: schemas.User, response: Response):
    with engine.connect() as conn:
        s = select(models.User).where(models.User.id == usr.id)
        res = conn.execute(s).all()
    if not res:
        em1 = models.User(id=usr.id, username=usr.username,
                          hashed_password=get_password_hash(usr.hashed_password))
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(em1)
        session.commit()
        return "SUCCESS"
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"


async def get_users(response: Response):
    with engine.connect() as conn:
        s = select(models.User)
        res = conn.execute(s)
    response.status_code = status.HTTP_200_OK
    return res.all()


async def get_users_obj():
    all_users = list()
    vals = await get_users(Response())
    for usr_vals in vals:
        temp_usr = models.User()
        temp_usr.__init_from_vals__(usr_vals)
        all_users.append(temp_usr)
    return all_users


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = await get_auth(token)
    token_data = TokenData(username=payload.get("sub"))
    db = await get_users_obj()
    print("DB IS: ", db)
    user = get_user_obj(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Invalid user")
    return current_user


async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


async def replace_user(usr: schemas.User, response: Response):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = session.query(models.User).filter_by(id=usr.id)[0]
    except IndexError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: USER NOT FOUND"
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: USER NOT FOUND"
    user.username = usr.username if usr.username else user.username
    user.full_name = usr.full_name if usr.full_name else user.full_name
    user.hashed_password = get_password_hash(usr.hashed_password)\
        if usr.hashed_password else user.hashed_password
    user.email = usr.email if usr.email else user.email
    user.disabled = usr.disabled if usr.disabled else user.disabled
    user.privilege = usr.privilege if usr.privilege else user.privilege
    session.add(user)
    session.commit()
    response.status_code = status.HTTP_200_OK
    return "OK"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_obj(db, username: str):
    for usr in db:
        if usr.username == username:
            return usr
    return None


def authenticate_user(db, username: str, password: str):
    user = get_user_obj(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_auth(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    return payload


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = await get_users_obj()
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username,
              "role": user.privilege
              },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}