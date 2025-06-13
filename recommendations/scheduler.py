# recommendations/scheduler.py
from celery import Celery
from celery.schedules import crontab
from .tasks import update_global_recommendations

app = Celery('library_project')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        update_global_recommendations.s(),
        name='Обновление глобальных рекомендаций'
    )