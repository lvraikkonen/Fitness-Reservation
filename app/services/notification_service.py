from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.deps import get_db


class NotificationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_notification(self, notification_id: int) -> Notification:
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification

    def get_notifications(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[Notification]:
        query = self.db.query(Notification)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def create_notification(self, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.dict())
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def update_notification(self, notification_id: int, notification: NotificationUpdate) -> Notification:
        db_notification = self.get_notification(notification_id)
        update_data = notification.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_notification, key, value)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def delete_notification(self, notification_id: int):
        db_notification = self.get_notification(notification_id)
        self.db.delete(db_notification)
        self.db.commit()
