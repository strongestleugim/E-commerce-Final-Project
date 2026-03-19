#!/usr/bin/env bash
set -euo pipefail

python -m flask --app run.py init-db
python -m flask --app run.py seed-db

exec gunicorn --bind "0.0.0.0:${PORT:-10000}" run:app
