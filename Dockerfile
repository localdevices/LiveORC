FROM python:3.11.8-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt /app/
WORKDIR /app

# install dependencies
RUN apt update
RUN apt install ffmpeg libsm6 libxext6 libgl1 python3-venv libgdal-dev libsqlite3-mod-spatialite -y

# setup application with database
RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt
# RUN python manage.py collectstatic
# RUN python manage.py migrate

COPY . /app/