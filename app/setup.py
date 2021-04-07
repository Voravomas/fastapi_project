import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# here we allow ourselves to pass interpolation vars to alembic.ini
# fron the host env
section = config.config_ini_section
config.set_section_option(section, "PSQL_LOG", os.environ.get('PSQL_LOG'))
config.set_section_option(section, "PSQL_PASS", os.environ.get('PSQL_LOG'))
config.set_section_option(section, "PSQL_URL", os.environ.get('PSQL_URL'))
config.set_section_option(section, "PSQL_DB_NAME", os.environ.get('PSQL_DB_NAME'))
