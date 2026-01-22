from pathlib import Path
import sys
import os

# ===========================================================
# BASE DEL PROYECTO
# ===========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


# ===========================================================
# SEGURIDAD
# ===========================================================

SECRET_KEY = 'django-insecure-ypg6$bf(wje26r1+m%@7di2h9i)_#6^pee+fjwdx13x337iidy'
DEBUG = True
#DEBUG = False
ALLOWED_HOSTS = ["*"]



# ===========================================================
# APPS
# ===========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'pedidos',
]


# ===========================================================
# MIDDLEWARE
# ===========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ===========================================================
# URLS
# ===========================================================

ROOT_URLCONF = 'imperyo.urls'


# ===========================================================
# TEMPLATES  ✔ CORREGIDO ✔
# ===========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",      # directorio de plantillas global
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ===========================================================
# WSGI
# ===========================================================

WSGI_APPLICATION = 'imperyo.wsgi.application'


# ===========================================================
# BASE DE DATOS
# ===========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ===========================================================
# VALIDACIÓN DE PASSWORDS (limpio para desarrollo)
# ===========================================================

AUTH_PASSWORD_VALIDATORS = []


# ===========================================================
# REGIÓN Y CONFIG LOCAL
# ===========================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ===========================================================
# ARCHIVOS ESTÁTICOS (CSS / JS / IMÁGENES / LOGO)
# ===========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',    # carpeta donde tienes el logo
]

# En producción activarías:
STATIC_ROOT = BASE_DIR / "staticfiles"


# ===========================================================
# AUTO ID
# ===========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===========================================================
# LOGIN / LOGOUT
# ===========================================================

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/pedidos/'
LOGOUT_REDIRECT_URL = '/admin/login/'
import os
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
