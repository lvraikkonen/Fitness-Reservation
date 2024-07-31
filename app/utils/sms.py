import httpx
from twilio.rest import Client
from app.core.config import settings, get_logger

logger = get_logger(__name__)


async def send_sms_async(phone_number: str, message: str):
    url = settings.SMS_API_URL
    payload = {
        "phone": phone_number,
        "message": message,
        "api_key": settings.SMS_API_KEY
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        logger.info(f"SMS sent successfully to {phone_number}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        # 在实际应用中，你可能想要记录这个错误或重新抛出异常


def send_sms_sync(phone: str, message: str) -> None:
    # 使用同步方式发送短信的逻辑
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        print(f"SMS sent to {phone}")
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        raise
