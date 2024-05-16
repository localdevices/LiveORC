FROM python:3.11.8-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt /liveorc/

# Get folder ready
ADD . /liveorc
WORKDIR /liveorc

# install dependencies
RUN apt update && apt install ffmpeg libsm6 libxext6 libgl1 python3-venv libgdal-dev libsqlite3-mod-spatialite nginx certbot gettext dos2unix cron -y && \
    # setup application with database
    pip install --upgrade pip && pip install --trusted-host pypi.python.org --requirement requirements.txt && pip install gunicorn && \
    # make scripts executable and run as unix
    dos2unix /liveorc/start.sh && dos2unix /liveorc/nginx/letsencrypt-autogen.sh && dos2unix /liveorc/nginx/crontab && \
    chmod +x /liveorc/start.sh && chmod +x /liveorc/nginx/letsencrypt-autogen.sh && chmod +x /liveorc/nginx/crontab && \
    # Setup cron
    ln -s /liveorc/nginx/crontab /var/spool/cron/crontabs/root && service cron start && \
    # make sure that any locally made migrations are not persisting in the volumes
    rm -fr /liveorc/users/migrations/* && rm -fr /liveorc/api/migrations/* && rm -fr /liveorc/data/* && \
    touch /liveorc/users/migrations/__init__.py && touch /liveorc/api/migrations/__init__.py && \
    python3 manage.py makemigrations --noinput && python3 manage.py migrate --noinput && \
    python3 manage.py collectstatic --noinput --skip-checks && \
    # upload the record with styling
    python3 manage.py loaddata ./django-admin-interface/admin_interface_theme_liveorc.json

# copy the nice style to the media volume
COPY django-admin-interface/media /liveorc/media

VOLUME /liveorc/data
VOLUME /liveorc/static
VOLUME /liveorc/api/migrations
VOLUME /liveorc/users/migrations

