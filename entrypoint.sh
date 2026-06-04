#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py load_demo_data
python manage.py collectstatic --noinput --clear 2>/dev/null || true

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

exec python manage.py runserver 0.0.0.0:8000
