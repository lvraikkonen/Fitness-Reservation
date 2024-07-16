from celery import Celery
from celery.schedules import crontab

celery_app = Celery('tasks', broker='amqp://guest@localhost//')

celery_app.conf.beat_schedule = {
    'create-future-venue-time-slots': {
        'task': 'app.tasks.venue_tasks.create_future_venue_time_slots',
        'schedule': crontab(hour=0, minute=0),  # 每天午夜执行
    },
}
