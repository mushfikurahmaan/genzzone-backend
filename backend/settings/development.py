"""
Development settings for backend project.

These settings are used for local development and testing.
"""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
# For development, using a default key. In production, use environment variable.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-x4e8=)t3jgk18lr%9+al-(-ct09c+kvinoqx_v-6ki0=b8vqt5')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - Allow localhost for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# Third-party API keys - using defaults for development
# In production, these should come from environment variables
STEADFAST_API_KEY = os.environ.get('STEADFAST_API_KEY', 'nqxfbgrq4qoug6s1o0hnyu5zaqd4wazf')
STEADFAST_SECRET_KEY = os.environ.get('STEADFAST_SECRET_KEY', 'erv9pfpeleiayb31x19xmaia')

