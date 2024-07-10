from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.schemas.reservation import ReservationRead
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

    def notify_user(self, user_id: int, title: str, content: str, type: str = "RESERVATIONS") -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=type
        )
        self.db.add(notification)
        self.db.commit()

        self.send_email(user.email, content)
        self.send_sms(user.phone, content)

    def send_email(self, email: str, message: str) -> None:
        # 在这里实现发送电子邮件的逻辑
        print(f"Sending email to {email}: {message}")

    def send_sms(self, phone: str, message: str) -> None:
        # 在这里实现发送短信的逻辑
        print(f"Sending SMS to {phone}: {message}")

    def send_reservation_reminder(self, reservation: ReservationRead) -> None:
        user = self.db.query(User).filter(User.id == reservation.user_id).first()
        if user:
            # 发送提醒通知给用户
            self.send_email(
                email=user.email,
                message=f"You have a reservation (ID: {reservation.id}) coming up soon!"
            )
            self.send_sms(
                phone=user.phone,
                message=f"Reminder: You have a reservation (ID: {reservation.id}) coming up soon!"
            )

    def send_reservation_cancellation_notice(self, reservation: ReservationRead) -> None:
        user = self.db.query(User).filter(User.id == reservation.user_id).first()
        if user:
            # 发送预约取消通知给用户
            self.send_email(
                email=user.email,
                message=f"Your reservation (ID: {reservation.id}) has been cancelled due to venue closure or time slot adjustment."
            )
            self.send_sms(
                phone=user.phone,
                message=f"Notice: Your reservation (ID: {reservation.id}) has been cancelled due to venue closure or time slot adjustment."
            )
