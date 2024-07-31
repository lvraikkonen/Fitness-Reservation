import aiosmtplib, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings, get_logger

logger = get_logger(__name__)


async def send_email_async(to_email: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        smtp = aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, use_tls=True)
        await smtp.connect()
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # 在实际应用中，你可能想要记录这个错误或重新抛出异常


def send_email_sync(to_email: str, subject: str, content: str) -> None:
    # 使用同步方式发送邮件的逻辑
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise
