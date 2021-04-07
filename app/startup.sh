#!/bin/sh

git pull
# python3 setup.py
alembic upgrade head

uvicorn main:app --host 0.0.0.0
