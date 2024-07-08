from mongoengine import Document, StringField, IntField, DateTimeField


class UserLog(Document):
    user_id = IntField(required=True)
    operation = StringField(required=True)
    timestamp = DateTimeField(required=True)
    details = StringField()

    meta = {
        'collection': 'user_logs',
        'indexes': [
            'user_id',
            'operation',
            'timestamp'
        ]
    }
