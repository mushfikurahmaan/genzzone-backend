"""
Production settings for backend project.

These settings are used in production deployment.
All sensitive values should come from environment variables.
"""
import os
import dj_database_url
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allowed hosts - should be set via environment variable
# Railway provides RAILWAY_PUBLIC_DOMAIN, or you can set ALLOWED_HOSTS
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')

if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
elif railway_domain:
    ALLOWED_HOSTS = [railway_domain, f'*.{railway_domain}']
else:
    # Fallback: allow all (not ideal, but allows deployment to proceed)
    ALLOWED_HOSTS = ['*']

# Database - Use DATABASE_URL (Railway standard) or fallback to individual variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback to individual database variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
    # Validate database settings only if using individual variables
    if not all([DATABASES['default']['NAME'], DATABASES['default']['USER'], DATABASES['default']['PASSWORD']]):
        raise ValueError("Either DATABASE_URL or database credentials (DB_NAME, DB_USER, DB_PASSWORD) must be set in production!")

# CORS - Configure allowed origins for production
cors_origins_env = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
else:
    # Allow all origins in development (you should set this in production!)
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Security settings for production
# Railway handles SSL, so we don't need to force redirect
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Third-party API keys - must come from environment variables
STEADFAST_API_KEY = os.environ.get('STEADFAST_API_KEY', '')
STEADFAST_SECRET_KEY = os.environ.get('STEADFAST_SECRET_KEY', '')

# Warn if not set, but don't fail (allows deployment to proceed)
if not STEADFAST_API_KEY or not STEADFAST_SECRET_KEY:
    import warnings
    warnings.warn("STEADFAST_API_KEY and STEADFAST_SECRET_KEY should be set in production!")

# Static files - configure for production (e.g., AWS S3, CloudFront, etc.)
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

