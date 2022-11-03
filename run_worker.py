import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()
from core.workers import NatsWorker

nats_worker = NatsWorker()
