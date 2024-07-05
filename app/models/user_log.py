from datetime import datetime
from app.db.mongo import db


class UserLog(db.Document):
    user_id = db.IntField(required=True)
    operation = db.StringField(required=True)
    details = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'user_logs'}
