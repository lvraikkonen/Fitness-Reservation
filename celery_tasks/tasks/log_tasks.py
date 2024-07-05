import json
from datetime import datetime, timedelta
from celery.schedules import crontab
from app.models.user_log import UserLog
from celery_tasks.celery_app import celery_app


@celery_app.task
def log_user_operation(user_id: int, operation: str, details: dict = None):
    # 敏感信息脱敏
    if details and 'password' in details:
        details['password'] = '*' * len(details['password'])

    log_data = {
        'user_id': user_id,
        'operation': operation,
        'details': json.dumps(details) if details else None
    }
    UserLog(**log_data).save()


@celery_app.task
def archive_logs():
    archive_date = datetime.utcnow() - timedelta(days=90)

    # 使用聚合管道优化数据迁移
    pipeline = [
        {
            '$match': {
                'timestamp': {'$lt': archive_date}
            }
        },
        {
            '$out': f"user_logs_archive_{archive_date.strftime('%Y%m')}"
        }
    ]

    # 使用批量插入优化数据迁移
    batch_size = 1000
    for i in range(0, UserLog.objects(timestamp__lt=archive_date).count(), batch_size):
        logs = UserLog.objects(timestamp__lt=archive_date).limit(batch_size).skip(i)
        UserLog._get_collection().aggregate(pipeline)
        logs.delete()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(day_of_month='1', hour='0', minute='0'),
        archive_logs.s(),
    )