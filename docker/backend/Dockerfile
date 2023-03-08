FROM registry.gitlab.com/auditor2/devops/images/opencv/core:22.10.080723
WORKDIR /app/
COPY Pipfile  /app/backend/
COPY Pipfile.lock /app/backend/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT=1
ENV IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg


WORKDIR /app/backend
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    libffi-dev \
    jpeg-dev zlib-dev libjpeg gettext \
    g++ \
    && pip install pipenv \
    && pipenv install --system --deploy --ignore-pipfile \
    && apk del build-deps
WORKDIR /app/
COPY . /app/
RUN mkdir -p ./backend/src/share \
    && mkdir -p ./backend/src/share/auditor-v2_media \
    && mkdir -p ./backend/src/share/auditor-v2_media/images \
    && mkdir -p ./backend/src/share/auditor-v2_media/video \
    && mkdir -p ./backend/src/share/auditor-v2_media/audio \
    && mkdir -p ./backend/src/share/auditor-v2_statics 
    # && touch "${APP_API_LOG}"
RUN addgroup app && adduser -S app -G app \
    && chown -R app:app /app/backend/

USER app
WORKDIR /app/backend
