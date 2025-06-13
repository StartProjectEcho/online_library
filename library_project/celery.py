# celery.py
from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')

app = Celery('library_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-global-recommendations': {
        'task': 'recommendations.tasks.update_global_recommendations',
        'schedule': crontab(hour=0, minute=0),  # Ежедневно
    },
    'generate-user-recommendations': {
        'task': 'recommendations.tasks.generate_recommendations_for_all_users',
        'schedule': timedelta(seconds=10),  # Каждые 10 секунд
    },
}