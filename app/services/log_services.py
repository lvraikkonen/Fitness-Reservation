import json
from datetime import datetime, timedelta
from app.models.user_log import UserLog
from celery_tasks.tasks.log_tasks import log_user_operation, archive_logs


def log_operation(user_id: int, operation: str, details: dict = None):
    log_data = {
        'user_id': user_id,
        'operation': operation,
        'details': json.dumps(details) if details else None
    }
    log_user_operation.delay(**log_data)


def get_user_logs(user_id: int, start_time: datetime = None, end_time: datetime = None, operation: str = None,
                  skip: int = 0, limit: int = 100):
    query = UserLog.objects(user_id=user_id)
    if start_time:
        query = query.filter(timestamp__gte=start_time)
    if end_time:
        query = query.filter(timestamp__lte=end_time)
    if operation:
        query = query.filter(operation=operation)

    logs = query.order_by('-timestamp').skip(skip).limit(limit)
    return logs


def get_all_logs(start_time: datetime = None, end_time: datetime = None, operation: str = None, skip: int = 0,
                 limit: int = 100):
    query = UserLog.objects
    if start_time:
        query = query.filter(timestamp__gte=start_time)
    if end_time:
        query = query.filter(timestamp__lte=end_time)
    if operation:
        query = query.filter(operation=operation)

    logs = query.order_by('-timestamp').skip(skip).limit(limit)
    return logs