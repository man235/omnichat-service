from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"] = env.db("DATABASE_URL")  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)

# STATIC
# ------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# MEDIA
# ------------------------------------------------------------------------------

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="SOP Chat Service <noreply@example.com>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[SOP Chat Service]",
)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL")

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]  # noqa F405
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.readthedocs.io/en/stable/esps
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ANYMAIL = {}


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# Your stuff...
# ------------------------------------------------------------------------------
FACEBOOK_APP_ID = '5482298951821522'     # 459417807935454
FACEBOOK_APP_SECRET = '14999c82309aff7a760b509c96c16b00'    # 316f7035fded8674d79148a130518ed0
FACEBOOK_GRAPH_API = 'https://graph.facebook.com/v14.0'
URL_FACEBOOK_GRAPH_API_SEND_MESSAGE = 'https://graph.facebook.com/me/messages'

# Zalo OA
ZALO_APP_ID = env(
    "ZALO_APP_ID", default="1244402066467636358"
)
ZALO_APP_SECRET_KEY = env(
    "ZALO_APP_SECRET_KEY", default="q9sESGTOXlld2ELXlxmE"
)
ZALO_OA_OAUTH_API = env(
    "ZALO_OA_OAUTH_API", default="https://oauth.zaloapp.com/v4/oa"
)
ZALO_OA_OPEN_API = env(
    "ZALO_OA_OPEN_API", default="https://openapi.zalo.me/v2.0/oa"
)
OA_ACCESS_EXPIRED_IN = env(
    "OA_ACCESS_EXPIRED_IN", default = 90000
)      # 25h
OA_REFRESH_EXPIRED_IN = env(
    "OA_REFRESH_EXPIRED_IN", default = 7889238
)    # 3m



CHANNELS_SUBSCRIBE = ["omniChat.message.receive.*"]

REDIS_HOST = '172.27.228.229'
REDIS_PORT = 6379
REDIS_PASSWORD = '02011993'
REDIS_USER = ''
REDIS_DB = 0

NATS_URL = "nats://172.24.222.112:4222"       # nats://42.116.253.17:4222
# NATS_URL = "nats://172.30.13.168:4222"       # nats://172.30.13.168:4222
PROFILE_USER_FIELDS = 'first_name,last_name,profile_pic,gender,locale,name,email'
SITE_ID = 1

DOMAIN_MINIO_SAVE_ATTACHMENT = "https://webhook.minhhv11.xyz/"

ELASTIC_SEARCH_URL = env(
    "ELASTIC_SEARCH_URL", default="http://172.24.222.113:9200"
)
ELASTIC_KIBANA_URL = env(
    "ELASTIC_KIBANA_URL", default="http://172.24.222.113:5601"
)
ELASTIC_USER = env(
    "ELASTIC_USER", default="dev"
)
ELASTIC_PASSWORD = env(
    "ELASTIC_PASSWORD", default="vA85m0^iAGfI"
)

ELASTIC_JOURNEY_LOGSTASH = env(
    'ELASTIC_JOURNEY_LOGSTASH', default="stg_customer_journey_logstash"
)
