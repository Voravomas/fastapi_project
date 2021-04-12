from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from fastapi import Response, status

import models
import schemas
from auth import get_password_hash


async def create_user(engine: Engine, usr: schemas.User, response: Response):
    with engine.connect() as conn:
        s = select(models.User).where(models.User.id == usr.id)
        res = conn.execute(s).all()
    if not res:
        em1 = models.User(id=usr.id, username=usr.username, hashed_password=get_password_hash(usr.hashed_password))
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(em1)
        session.commit()
        return "SUCCESS"
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"
