FROM python:3.11.8-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt /liveorc/
WORKDIR /liveorc

# install dependencies
RUN apt update
RUN apt install ffmpeg libsm6 libxext6 libgl1 python3-venv libgdal-dev libsqlite3-mod-spatialite nginx certbot gettext -y

# setup application with database
RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt

RUN pip install gunicorn

COPY . /liveorc/
# make scripts executable
RUN chmod +x /liveorc/start.sh
RUN chmod +x /liveorc/nginx/letsencrypt-autogen.sh
RUN python3 manage.py collectstatic --noinput
RUN python3 manage.py migrate --noinput
# copy the nice liveorc style files
COPY ./django-admin-interface/media /liveorc/media
# upload the record with styling
RUN python3 manage.py loaddata ./django-admin-interface/admin_interface_theme_liveorc.json
VOLUME /liveorc/media