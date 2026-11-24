#!/bin/sh
set -e

# migrate va collectstatic faqat web (gunicorn) ishga tushganda
if [ "$1" = "gunicorn" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
fi

exec "$@"