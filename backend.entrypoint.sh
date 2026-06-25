#!/bin/sh

set -e

POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_WAIT_TIMEOUT="${POSTGRES_WAIT_TIMEOUT:-30}"

REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_WAIT_TIMEOUT="${REDIS_WAIT_TIMEOUT:-30}"

echo 'Waiting for PostgreSQL...'

for i in $(seq 1 "$POSTGRES_WAIT_TIMEOUT"); do
  if nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; then
    echo 'PostgreSQL is ready.'
    break
  fi

  echo "Waiting... ($i/$POSTGRES_WAIT_TIMEOUT)"
  sleep 1

  if [ "$i" -eq "$POSTGRES_WAIT_TIMEOUT" ]; then
    echo 'PostgreSQL did not start in time.'
    exit 1
  fi
done

echo 'Waiting for Redis...'

for i in $(seq 1 "$REDIS_WAIT_TIMEOUT"); do
  if nc -z "$REDIS_HOST" "$REDIS_PORT"; then
    echo 'Redis is ready.'
    break
  fi

  echo "Waiting... ($i/$REDIS_WAIT_TIMEOUT)"
  sleep 1

  if [ "$i" -eq "$REDIS_WAIT_TIMEOUT" ]; then
    echo 'Redis did not start in time.'
    exit 1
  fi
done

if [ "$1" = "gunicorn" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput

  if [ "$DJANGO_CREATE_SUPERUSER" = "True" ] || \
     [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    python manage.py createsuperuser --noinput || true
  fi
fi

exec "$@"