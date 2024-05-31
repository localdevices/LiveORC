""" Celery settings for app. """

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import nodeorc

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LiveORC.settings')

app = Celery(
    'LiveORC',
)

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered nodeorc tasks.
app.autodiscover_tasks()
