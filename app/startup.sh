#!/bin/sh

# pulling any new changes
git pull

# config DB
alembic upgrade head

# start FastAPI
uvicorn main:app --host 0.0.0.0
