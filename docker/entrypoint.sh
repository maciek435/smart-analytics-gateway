#!/bin/sh
set -e

echo ">> Migracje bazy danych..."
alembic upgrade head

if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo ">> Tworzenie konta admina (jeśli jeszcze nie istnieje)..."
  python -m app.scripts.create_admin
fi

echo ">> Start API..."
exec "$@"