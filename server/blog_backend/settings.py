import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def env(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and (value is None or value == ''):
        raise RuntimeError(f'Missing required environment variable: {key}')
    return value


SECRET_KEY = env('DJANGO_SECRET_KEY', required=True)

DEBUG = env('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [h.strip() for h in env('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'blog_backend.urls'
WSGI_APPLICATION = 'blog_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME', required=True),
        'USER': env('DB_USER', required=True),
        'PASSWORD': env('DB_PASSWORD', required=True),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.utils.api_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

CORS_ALLOWED_ORIGINS = [o.strip() for o in env('CLIENT', '').split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

JWT_SECRET = env('JWT_SECRET', required=True)
JWT_ALGORITHM = 'HS256'

COOKIE_OPTIONS = {
    'max_age': 15 * 24 * 60 * 60,
    'samesite': 'None',
    'httponly': True,
    'secure': True,
}
SHORT_COOKIE_MAX_AGE = 60 * 15

USE_TZ = True
TIME_ZONE = 'UTC'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
