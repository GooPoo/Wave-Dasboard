import os
import environ
from pathlib import Path

ALLOWED_HOSTS = ['54.253.180.26', 'localhost', '127.0.0.1']

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(PROJECT_PATH, '.env'))

DEBUG = env.bool('DEBUG', default=False)

PREDICTIONS_PATH= env.str('PREDICTIONS_PATH', default='')
FORECASTS_PATH=env.str('FORECASTS_PATH', default='')
BUOY_PATH=env.str('BUOY_PATH', default='')
WIND_PATH =env.str('WIND_PATH', default='')
LOG_PATH=env.str('LOG_PATH', default='')
CSV_PATH=env.str('CSV_PATH', default='')



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'database.sqlite'),
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(PROJECT_PATH, 'static')]
STATIC_ROOT = os.path.join(PROJECT_PATH, 'staticfiles')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TIME_ZONE = 'Australia/Perth'

with open(BASE_DIR / "secret__key.txt") as f:
    SECRET_KEY = f.read().strip()

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'user_sessions',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_email',
    'two_factor',
    'two_factor.plugins.phonenumber',
    'two_factor.plugins.email',
    'backend',
    'werkzeug_debugger_runserver',
    'django_extensions',
    'debug_toolbar',
    'bootstrapform'
]

LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'two_factor:profile'
INTERNAL_IPS = ('127.0.0.1',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

TWO_FACTOR_CALL_GATEWAY = 'example.gateways.Messages'
TWO_FACTOR_SMS_GATEWAY = 'example.gateways.Messages'
PHONENUMBER_DEFAULT_REGION = 'NL'
TWO_FACTOR_REMEMBER_COOKIE_AGE = 120  # Set to 2 minute for testing
TWO_FACTOR_WEBAUTHN_RP_NAME = 'Demo Application'
SESSION_ENGINE = 'user_sessions.backends.db'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@example.org'
SILENCED_SYSTEM_CHECKS = ['admin.E410']

try:
    from .settings_private import *  # noqa
except ImportError:
    pass

