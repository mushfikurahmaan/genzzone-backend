"""
Django settings for backend project.
Production-ready configuration - all sensitive values from environment variables.
"""
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allowed hosts
ALLOWED_HOSTS = [os.environ.get('RAILWAY_PUBLIC_DOMAIN', '*')]

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600)
}

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'storages',  # For R2 storage (S3-compatible)
    'products',
    'orders',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins (required for Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') 
    if origin.strip()
]
# Add Railway domain if available
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if railway_domain and railway_domain != '*':
    # Handle both formats: with or without https://
    if railway_domain.startswith('http://') or railway_domain.startswith('https://'):
        railway_url = railway_domain
    else:
        railway_url = f"https://{railway_domain}"
    if railway_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_url)

# Security settings
SECURE_SSL_REDIRECT = False
# Only use secure cookies if we're sure we're on HTTPS
USE_HTTPS = os.environ.get('USE_HTTPS', 'True').lower() == 'true'

# CSRF Configuration - CRITICAL for cross-origin subdomain requests
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF, not session-based
CSRF_COOKIE_NAME = 'csrftoken'  # Explicit cookie name
CSRF_COOKIE_SECURE = USE_HTTPS  # Use secure flag in production
CSRF_COOKIE_SAMESITE = 'None'  # Required for cross-origin requests
CSRF_COOKIE_DOMAIN = '.genzzone.com'  # Share cookie across subdomains (note the leading dot)
CSRF_COOKIE_PATH = '/'  # Cookie available on all paths

# Session Configuration
SESSION_COOKIE_SECURE = USE_HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-origin requests
SESSION_COOKIE_DOMAIN = '.genzzone.com'  # Share session across subdomains
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Additional Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Third-party API keys
STEADFAST_API_KEY = os.environ.get('STEADFAST_API_KEY')
STEADFAST_SECRET_KEY = os.environ.get('STEADFAST_SECRET_KEY')

# Admin URL path (for security - use a custom path in production)
ADMIN_URL_PATH = os.environ.get('ADMIN_URL_PATH', 'admin/')


# ========= Cloudflare R2  =========

# AWS S3/R2 Configuration
AWS_ACCESS_KEY_ID = os.environ["R2_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["R2_BUCKET_NAME"]

AWS_S3_ENDPOINT_URL = f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"

AWS_S3_REGION_NAME = "auto"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "virtual"

AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_S3_CUSTOM_DOMAIN = "media.genzzone.com"
MEDIA_URL = "https://media.genzzone.com/"

# Django 4.2+ storage configuration (replaces DEFAULT_FILE_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}