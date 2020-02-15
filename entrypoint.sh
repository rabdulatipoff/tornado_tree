#!/bin/bash
set -euo pipefail

cd tornado_tree/

env PGPASSWORD=$APP_DB_PASSWORD psql -v ON_ERROR_STOP=1 -U "$APP_DB_USERNAME" -h $APP_DB_HOSTNAME -p $APP_DB_PORT -d $APP_DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS ltree;'

if [ -v MIGRATE ]; then
    alembic upgrade head
fi

exec python entry.py 
