from alembic.config import Config
from os import getenv


def get_path():
	return "postgresql://{}:{}@{}/{}".format(getenv('PSQL_LOG'),\
						getenv('PSQL_PASS'),\
						getenv('PSQL_URL'),\
						getenv('PSQL_DB_NAME'))


alembic_cfg = Config()
path = get_path()
alembic_cfg.set_main_option("sqlalchemy.url", path)
