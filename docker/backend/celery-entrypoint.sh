#!/bin/sh
$counterb
until cd /app/backend/src
do
echo "Waiting for volume to be ready..."
    if [ "$counterb" -gt 3 ];
    then
        echo "Exiting loop!"
        exit 1
    else
        counterb=$((counterb+1))
        sleep 1
    fi
done
if  [ "$ENVIRONMENT" != "local" ];
then
    mkdir -p ./backend/src/share \
         ./backend/src/share/auditor-v2_media \
         ./backend/src/share/auditor-v2_media/images \
         ./backend/src/share/auditor-v2_media/video \
         ./backend/src/share/auditor-v2_media/audio \
         ./backend/src/share/auditor-v2_statics

    touch "${APP_API_LOG}"
fi
celery -A django_celery worker -l info
