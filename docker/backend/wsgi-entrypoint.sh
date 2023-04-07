#!/bin/sh

$counter
until cd /app/backend/src
do
    echo "Waiting for volume to be ready..."
    if [ "$counter" -gt 3 ];
    then
        echo "Exiting loop!"

        exit 1
    else
        counter=$((counter+1))
        sleep 1
    fi
done
if [ "$ENVIRONMENT" != "local" ];
then
    mkdir -p share
    mkdir -p share/auditor-v2_media
    mkdir -p share/auditor-v2_media/images
    mkdir -p share/auditor-v2_media/video
    mkdir -p share/auditor-v2_media/audio
    mkdir -p share/auditor-v2_statics
    touch "${APP_API_LOG}"
fi
counter=0
until python3 ./manage.py showmigrations && python3 ./manage.py migrate
do
    echo "Waiting for db to be ready..."
    if [ "$counter" -gt 5 ];
    then
        echo "Exiting loop!"
        exit 2
    else
        counter=$((counter+1))
        sleep 1
    fi
done
if [ "$ENVIRONMENT" = "local" ]
then
  DEBUG=True python3 ./manage.py runserver 0.0.0.0:8000
else
  python3 ./manage.py collectstatic --noinput

  gunicorn asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS_NUMBER:-1}" \
  --threads "${GUNICORN_THREADS_NUMBER:-1}" \
  --log-level "${GUNICORN_LOG_LEVEL:-debug}"
fi
#####################################################################################
# Options to DEBUG Django server
# Optional commands to replace abouve gunicorn command

# Option 1:
# run gunicorn with debug log level
# gunicorn server.wsgi --bind 0.0.0.0:8000 --workers 1 --threads 1 --log-level debug

# Option 2:
# run development server
# DEBUG=True ./manage.py runserver 0.0.0.0:8000
