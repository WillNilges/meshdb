"""
Django settings for meshdb project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Log users out automatically after 2 days
SESSION_COOKIE_AGE = 172800  # Expire sessions after 2 Days. "1209600(2 weeks)" by default
SESSION_SAVE_EVERY_REQUEST = True  # "False" by default

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "DEBUG" in os.environ
PROFILING_ENABLED = DEBUG and not os.environ.get("DISABLE_PROFILING", "False") == "True"

ALLOWED_HOSTS = [
    "db.grandsvc.mesh.nycmesh.net",
    "db.grandsvc.mesh",
    "db.mesh.nycmesh.net",
    "db.mesh",
    "db.nycmesh.net",
    "127.0.0.1",
    "meshdb",
    "nginx",
    "host.docker.internal",
]

# FIXME: Shit works, but also doesn't(?) work with the ^ as the first character
# r"^https://\w+\.nycmesh\.net$",
# r"^http://\w+\.nycmesh\.net$",
CORS_ALLOWED_ORIGINS = [
    "http://forms.grandsvc.mesh.nycmesh.net",
    "https://forms.grandsvc.mesh.nycmesh.net",
    "http://map.grandsvc.mesh.nycmesh.net",
    "https://map.grandsvc.mesh.nycmesh.net",
    "http://map.grandsvc.mesh",
    "https://map.grandsvc.mesh",
    "http://forms.grandsvc.mesh",
    "https://forms.grandsvc.mesh",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:80",
    "http://localhost:80",
]

CSRF_TRUSTED_ORIGINS = [
    "http://db.grandsvc.mesh.nycmesh.net",
    "https://db.grandsvc.mesh.nycmesh.net",
    "http://db.grandsvc.mesh",
    "https://db.grandsvc.mesh",
    "http://127.0.0.1:8080",
    "http://meshdb:8081",
    "http://nginx:8080",
]

# Application definition

INSTALLED_APPS = [
    "meshdb.apps.MeshDBAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_hooks",
    "rest_framework",
    "rest_framework.authtoken",
    "meshapi",
    "meshapi_hooks",
    "meshweb",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_jsonform",
    "dbbackup",
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


if PROFILING_ENABLED:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")
    MIDDLEWARE.append("django_cprofile_middleware.middleware.ProfilerMiddleware")

DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

ROOT_URLCONF = "meshdb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "meshdb/templates"), os.path.join(BASE_DIR, "meshapi/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "meshdb.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}

# django-dbbackup
# https://django-dbbackup.readthedocs.io/en/master/installation.html

DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DBBACKUP_STORAGE_OPTIONS = {
    "bucket_name": os.environ.get("BACKUP_S3_BUCKET_NAME"),
    "location": os.environ.get("BACKUP_S3_BASE_FOLDER"),
}

DBBACKUP_CONNECTORS = {
    "default": {
        # "SINGLE_TRANSACTION": False,
        "IF_EXISTS": True
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True

LOGOUT_REDIRECT_URL = "/admin/login/"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    # BASE_DIR / "static", # The STATICFILES_DIRS setting should not contain the STATIC_ROOT setting
    "/var/www/static/",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

HOOK_EVENTS = {
    "building.created": "meshapi.Building.created+",
    "member.created": "meshapi.Member.created+",
    "install.created": "meshapi.Install.created+",
    "building.updated": "meshapi.Building.updated+",
    "member.updated": "meshapi.Member.updated+",
    "install.updated": "meshapi.Install.updated+",
    "building.deleted": "meshapi.Building.deleted+",
    "member.deleted": "meshapi.Member.deleted+",
    "install.deleted": "meshapi.Install.deleted+",
}

HOOK_SERIALIZERS = {
    "meshapi.Building": "meshapi.serializers.model_api.BuildingSerializer",
    "meshapi.Member": "meshapi.serializers.model_api.MemberSerializer",
    "meshapi.Install": "meshapi.serializers.model_api.InstallSerializer",
}

HOOK_CUSTOM_MODEL = "meshapi_hooks.CelerySerializerHook"

SPECTACULAR_SETTINGS = {
    "TITLE": "MeshDB Data API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "API Status", "description": "Meta-endpoint to indicate API status"},
        {"name": "Members", "description": "Members of the mesh and their contact details"},
        {"name": "Buildings", "description": "Buildings on the mesh and their location data, one per street address"},
        {
            "name": "Installs",
            "description": "Installs, one corresponding to each household that is either already on the mesh, "
            "or wishes to join the mesh",
        },
        {
            "name": "Nodes",
            "description": "Nodes, one corresponding to each collection of devices with the same network number, "
            "the installs that use those devices, and the buildings that house them",
        },
        {"name": "Links", "description": "Network links between devices"},
        {
            "name": "Devices",
            "description": "Devices, one corresponding to each physical device on the mesh (routers, aps, cpes, etc.). "
            "Includes all Sectors",
        },
        {
            "name": "Sectors",
            "description": 'Special devices with antennas with broad coverage of a radial "slice" of land area. '
            "See https://docs.nycmesh.net/hardware/liteap/",
        },
        {"name": "Geographic & KML Data", "description": "Endpoints for geographic and KML data export"},
        {
            "name": "Website Map Data",
            "description": "Endpoints used to power the nycmesh.net website map. "
            "Uses a legacy data format, not recommended for new applications",
        },
        {
            "name": "Legacy Query Form",
            "description": "Endpoints used to power the legacy docs query form. "
            "Uses a legacy data format, not recommended for new applications",
        },
        {"name": "User Forms", "description": "Forms exposed directly to humans"},
    ],
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": 10,
        "defaultModelExpandDepth": 10,
        "displayRequestDuration": True,
        "docExpansion": "none",
    },
}

IMPORT_EXPORT_IMPORT_PERMISSION_CODE = "add"
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = "view"
