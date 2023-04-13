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
mkdir -p share
chmod -R 777 share
touch "${APP_API_LOG}"
