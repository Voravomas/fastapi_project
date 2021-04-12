from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from os import getenv


# creating base
Base = declarative_base()


def get_path():
    return "postgresql://{}:{}@{}/{}".format(getenv('PSQL_LOG'),
                                             getenv('PSQL_PASS'),
                                             getenv('PSQL_URL'),
                                             getenv('PSQL_DB_NAME'))


# Engine
db_path = get_path()
engine = create_engine(db_path, echo=True, future=True)
