from celery_tasks.celery_app import celery_app
from app.utils.email import send_email_async
from app.utils.sms import send_sms_async


@celery_app.task(name='celery_tasks.tasks.notification_tasks.send_email')
def send_email_task(email: str, subject: str, content: str):
    send_email_async(email, subject, content)


@celery_app.task(name='celery_tasks.tasks.notification_tasks.send_sms')
def send_sms_task(phone: str, content: str):
    send_sms_async(phone, content)
