from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="G7SkvKOQpW2Fmw6EreqaLP52au4EKHvk4cu8OP2OMRVuwpRArEQNaKULGlvoJTf4",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405
# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = ['*']
FACEBOOK_APP_ID = '5482298951821522'     # 459417807935454
FACEBOOK_APP_SECRET = '14999c82309aff7a760b509c96c16b00'    # 316f7035fded8674d79148a130518ed0
FACEBOOK_GRAPH_API = 'https://graph.facebook.com/v14.0'
URL_FACEBOOK_GRAPH_API_SEND_MESSAGE = 'https://graph.facebook.com/me/messages'


# ZALO_APP_ID = '1910014910662737087'
# ZALO_APP_SECRET_KEY = 'C88Hy3I4wq4CSAC2H3bU'
# ZALO_OA_OAUTH_API = 'https://oauth.zaloapp.com/v4/oa'
# ZALO_OA_OPEN_API = 'https://openapi.zalo.me/v2.0/oa'
# OA_ACCESS_EXPIRED_IN = 90000      # 25h
# OA_REFRESH_EXPIRED_IN = 7889238    # 3m


# Zalo OA
ZALO_APP_ID = env(
    "ZALO_APP_ID", default="1910014910662737087"
)
ZALO_APP_SECRET_KEY = env(
    "ZALO_APP_SECRET_KEY", default="C88Hy3I4wq4CSAC2H3bU"
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

REDIS_HOST = env(
    "REDIS_HOST", default="172.24.222.112"
)
REDIS_PORT = env(
    "REDIS_PORT", default="6379"
)
REDIS_PASSWORD = env(
    "REDIS_PASSWORD", default="redisPassword"
)
REDIS_USER = env(
    "REDIS_USER", default=""
)
REDIS_DB = env(
    "REDIS_DB", default=1
)


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = "Bn6aG5NeEcpSCCAx"
AWS_SECRET_ACCESS_KEY = "bfHx6nlrqrddWH5uT4axHJ3HCMZ1e1Zg"
AWS_STORAGE_BUCKET_NAME = "sop-local"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

if DEBUG:
    AWS_S3_ENDPOINT_URL = "http://172.24.222.114:9000"

DOMAIN_MINIO_SAVE_ATTACHMENT = "https://webhook.minhhv11.xyz/"
PROFILE_USER_FIELDS = 'first_name,last_name,profile_pic,gender,locale,name,email'
SITE_ID = 1
NATS_URL = env(
    "NATS_URL", default="nats://172.24.222.112:4222"
)


# -----------------SENTINEL & REDIS-----------------
SENTINEL_NAMESPACE = 'ThienHi'
SENTINEL_URLS = [
    ('172.24.222.112' , 6379, ),
    # ('172.19.0.2' , 6379, ),
]
SENTINEL_PASSWORD = 'redisPassword'
SENTINEL_DECODE_RESPONSE = True
SENTINEL_DB = 1
