#!/bin/sh

# waiting for db to start
# echo "Waiting for db to init"
# sleep 5

# pulling any new changes
git pull

# config DB
alembic upgrade head

# start FastAPI
uvicorn main:app --host 0.0.0.0
