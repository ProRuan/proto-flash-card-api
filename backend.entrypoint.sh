#!/bin/sh

set -e

echo 'Waiting for PostgreSQL...'

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo 'PostgreSQL is ready.'

echo 'Waiting for Redis...'

while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done

echo 'Redis is ready.'

if [ "$1" = "gunicorn" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput

  if [ "$DJANGO_CREATE_SUPERUSER" = "True" ] || \
     [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    python manage.py createsuperuser --noinput || true
  fi
fi

exec "$@"