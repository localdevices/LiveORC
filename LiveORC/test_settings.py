# Import all settings from the main settings
from LiveORC.settings import *

# Override for testing
MEDIA_ROOT = None  # Will be set by pytest fixture, but we can set a temp dir here if needed
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': ':memory:',  # Use in-memory database for tests
    }
}

# Use a temporary directory for media
import tempfile
MEDIA_ROOT = tempfile.gettempdir() + '/liveorc_test_media'
MEDIA_URL = '/media/'

# Disable logging during tests (optional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}