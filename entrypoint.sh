#!/bin/bash
set -euo pipefail

cd tornado_tree/

if [ -v MIGRATE ]; then
    alembic upgrade head
fi

exec python entry.py 
