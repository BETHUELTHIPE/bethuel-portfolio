import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')

app = Celery('portfolio')

# Read CELERY_ settings from Django settings with a namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):  # pragma: no cover
    print(f'Request: {self.request!r}')
