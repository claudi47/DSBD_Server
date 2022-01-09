#!/usr/bin/env sh

set -e

python ./manage.py migrate --database=betdata
python ./manage.py migrate --database=parser
exec python ./manage.py runserver 0.0.0.0:8000 "$@"