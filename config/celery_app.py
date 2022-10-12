import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

disable_nat_in_celery_beat = os.environ.get("SOP_DISABLE_SUBSCRIBE_NAT_IN_CELERYBEAT")
if disable_nat_in_celery_beat == "true":
    _include = []
else:
    _include = ['core.nats']

app = Celery("sop_chat_service", include=_include)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
