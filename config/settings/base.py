"""
Django settings for config project.
"""

from pathlib import Path
from decouple import config as env_config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env_config('SECRET_KEY')
DEBUG = env_config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = env_config('ALLOWED_HOSTS', default='localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework_simplejwt",
    "core",
    "apps.users"
]
AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_config('POSTGRES_DB'),
        'USER': env_config('POSTGRES_USER'),
        'PASSWORD': env_config('POSTGRES_PASSWORD'),
        'HOST': env_config('POSTGRES_HOST'),
        'PORT': env_config('POSTGRES_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # Envelope renderer — wraps EVERY response in {status, message, data},
    # even ones that skip APIResponse manually. See core/renderers.py
    "DEFAULT_RENDERER_CLASSES": [
        "core.renderers.EnvelopeJSONRenderer",
    ],

    # Catches every raised exception (custom or DRF's own) and reshapes
    # it into the same envelope. See core/exception_handlers.py
    "EXCEPTION_HANDLER": "core.exception_handlers.custom_exception_handler",

    # Applies to every list endpoint by default (page, pages, page_size,
    # next, previous — nested under "pagination" in the response).
    # See core/pagination.py
    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    "PAGE_SIZE": 20,

    # Auth: JWT will plug in here on Day 3 — placeholder for now
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Day 3
    ],

    # Locked down by default — individual views override this with
    # IsOwner / IsOrganizer / IsAdmin from core/permissions.py as needed
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    # Global throttle — applies to every endpoint automatically.
    # BurstRateThrottle is intentionally NOT listed here; attach it
    # per-view only on sensitive endpoints (login, OTP, payments).
    "DEFAULT_THROTTLE_CLASSES": [
        "core.throttling.SustainedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "burst": "10/min",
        "sustained": "1000/day",
    },
}

from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes = 30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}