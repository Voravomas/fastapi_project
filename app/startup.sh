#!/bin/sh

git pull

alembic upgrade head

uvicorn main:app --host 0.0.0.0