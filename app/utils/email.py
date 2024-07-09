import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to_email: str, subject: str, body: str):
    # 创建 MIMEMultipart 对象
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, 'plain'))

    try:
        # 创建 SMTP 会话
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            # 如果使用 TLS，启用它
            if settings.SMTP_TLS:
                server.starttls()

            # 登录到 SMTP 服务器
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

            # 发送邮件
            server.send_message(msg)

        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {str(e)}")
        return False


def send_reset_password_email(email: str, username: str, reset_link: str):
    subject = "Password Reset Request"
    body = f"""
    Dear {username},

    You have requested to reset your password. Please click on the link below to reset your password:

    {reset_link}

    If you did not request this, please ignore this email.

    Best regards,
    Your App Team
    """

    return send_email(email, subject, body)
