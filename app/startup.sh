#!/bin/sh

# waiting for db to start
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $PSQL_URL -U $POSTGRES_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# pulling any new changes
git pull

# config DB
alembic upgrade head

# start FastAPI
uvicorn main:app --host 0.0.0.0
