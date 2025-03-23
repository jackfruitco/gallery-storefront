import os
from pathlib import Path

from core.config import configure_s3

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-ny+o5v-y861n+kguypqq2)ivq89wym@+e0fm5d)l1qx968ehc&",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (os.getenv("DJANGO_DEBUG", "false").lower() == "true") else False

# Set Allowed Hosts
if (hosts := os.getenv("DJANGO_ALLOWED_HOSTS", None)) is not None:
    ALLOWED_HOSTS = hosts.split(", ")

# CSRF Configuration
if (origins := os.getenv("CSRF_TRUSTED_ORIGINS", None)) is not None:
    CSRF_TRUSTED_ORIGINS = origins.split(", ")

CSRF_COOKIE_SECURE = (
    True if (os.getenv("CSRF_COOKIE_SECURE", "true").lower() == "true") else False
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "main",
    "gallery",
    "store",
    "shopify_app",
    "imagekit",
]

MIDDLEWARE = [
    "main.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "shopify_app.middleware.LoginProtection",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shopify_app.context_processors.shopify_custom",
                "store.context_processors.store",
                "main.context_processors.main",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": configure_s3(
            location=os.getenv("CLOUDFLARE_R2_DEFAULT_LOCATION", ""),
        ),
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Currently Configured Databases: Postgres (default), SQLite
# Database engine can be chosen via environment variable "DATABASE"
if (db_engine := os.getenv("DATABASE", None)) == "sqlite3":
    default = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
# elif db_engine == "":
else:
    default = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "AppDatabase"),
        "USER": os.getenv("DB_USER", "appuser"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }

DATABASES = {"default": default}

LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "handlers": ["console"],
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files (uploaded by users)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
