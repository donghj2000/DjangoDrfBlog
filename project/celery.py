from celery import Celery
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
app = Celery("django")
app.conf.update(
    broker_url="redis://127.0.0.1:6379/1",
)

app.autodiscover_tasks(settings.INSTALLED_APPS)