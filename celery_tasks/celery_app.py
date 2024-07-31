from celery import Celery
from celery.schedules import crontab

celery_app = Celery('tasks', broker='amqp://guest@localhost//')

# 包含所有任务模块
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    include=[
        'celery_tasks.tasks.log_tasks',
        'celery_tasks.tasks.venue_tasks',
        'celery_tasks.tasks.notification_tasks'
    ]
)

# 设置定期任务
celery_app.conf.beat_schedule = {
    'create-future-venue-time-slots': {
        'task': 'celery_tasks.tasks.venue_tasks.create_future_venue_time_slot',
        'schedule': crontab(hour=0, minute=0),  # 每天午夜执行
    },
    'archive-logs': {
        'task': 'celery_tasks.tasks.log_tasks.archive_logs',
        'schedule': crontab(day_of_month='1', hour='0', minute='0'),  # 每月1日午夜执行
    },
}


# 在 Celery 应用配置完成后设置周期性任务
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # 这里可以添加其他需要在配置后设置的周期性任务
    pass


if __name__ == '__main__':
    celery_app.start()
