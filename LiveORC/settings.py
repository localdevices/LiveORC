"""
Django settings for LiveORC project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import datetime
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# try to get BASE_DIR from env variable
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBASE_DIR = os.getenv("DJANGO_DBASE_DIR")

if not DBASE_DIR:
    DBASE_DIR = os.path.join(BASE_DIR, 'data')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "some-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("LORC_DEBUG", "NO").lower() == "YES".lower()

if DEBUG:
    print(f"LiveORC is in DEBUG mode. WARNING! DEBUG model is not suitable and secure for production.")

HOSTS = os.getenv("LORC_HOST")
ALLOWED_HOSTS = [] if HOSTS is None else HOSTS.split(",")
# ALLOWED_HOSTS = []  # default django project code
# if DEBUG:
ALLOWED_HOSTS = ["*"]
# Application definition

INSTALLED_APPS = [
    'users',
    "admin_interface",
    "colorfield",
    # 'django.contrib.admin',
    'LiveORC.admin.CustomAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django_json_widget',
    'rest_framework',
    'api',
    'rangefilter',
    'drf_spectacular',
    'fontawesomefree',
    'django_object_actions',
    'django_filters',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

SIMPLE_JWT = {
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=3650),
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(hours=6),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Celery Configuration Options
CELERY_BROKER_URL = f'amqp://{os.getenv("LORC_RABBITMQ_USER")}:{os.getenv("LORC_RABBITMQ_PASS")}@{os.getenv("LORC_RABBITMQ_HOST")}:5672/'
CELERY_RESULT_BACKEND = f'rcp://{os.getenv("LORC_RABBITMQ_USER")}:{os.getenv("LORC_RABBITMQ_PASS")}@{os.getenv("LORC_RABBITMQ_HOST")}:5672/'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# use modals instead of popups for django-admin-interface
X_FRAME_OPTIONS = "SAMEORIGIN"


ROOT_URLCONF = 'LiveORC.urls'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates/'),
            MEDIA_ROOT,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'api.context_processors.version_processor',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MEDIA_URL = '/media/'
THUMBSIZE = 50  # SIZE OF THUMBNAILS
WSGI_APPLICATION = 'LiveORC.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
if os.getenv("LORC_DB_HOST"):
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('LORC_DB_ENGINE', 'django.contrib.gis.db.backends.postgis'),
            'NAME': 'liveorc',
            'USER': os.getenv('LORC_DB_USER'),
            'PASSWORD': os.getenv('LORC_DB_PASS'),
            'HOST': os.getenv('LORC_DB_HOST', 'db'),
            'PORT': os.getenv('LORC_DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.spatialite',
            'NAME': os.path.join(DBASE_DIR, 'db.sqlite3'),
        }
    }


SPECTACULAR_SETTINGS = {
    'TITLE': 'LiveORC API',
    'DESCRIPTION': 'Live OpenRiverCam REST API and administrator dashboard',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_ROOT = os.path.join(BASE_DIR, "static")

AUTH_USER_MODEL = "users.User"

storage_url = os.getenv("LORC_STORAGE_HOST")
storage_port = os.getenv("LORC_STORAGE_PORT", 9000)

STORAGES = {
    # default storage is used for media files of installed apps (not our own)
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {},
    },
    "staticfiles": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": os.path.join(BASE_DIR, "static"),
            "base_url": "/static/",
        },
    }
}
if storage_url:
    # provide a bucket as media storage for our app
    STORAGES["media"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "endpoint_url": f"{storage_url}:{storage_port}",
            "access_key": os.getenv("LORC_STORAGE_ACCESS"),
            "secret_key": os.getenv("LORC_STORAGE_SECRET"),
            "bucket_name": "media"
        },
    }
else:
    # use the same as default
    STORAGES["media"] = STORAGES["default"]

if "win" in sys.platform:
    GDAL_LIBRARY_PATH = "gdal"
