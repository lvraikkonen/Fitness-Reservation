from mongoengine import connect
from app.core.config import mongo_settings

db = connect(
    db=mongo_settings.MONGO_DATABASE,
    host=mongo_settings.MONGO_HOST,
    port=mongo_settings.MONGO_PORT,
    username=mongo_settings.MONGO_USER,
    password=mongo_settings.MONGO_PASSWORD,
    authentication_source=mongo_settings.MONGO_AUTH_SOURCE,
)
