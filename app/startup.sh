#!/bin/sh

# waiting for db to start
echo "Waiting for DB to start"
sleep 5

# pulling any new changes
git pull

# config DB
alembic upgrade head

# start FastAPI
uvicorn main:app --host 0.0.0.0
