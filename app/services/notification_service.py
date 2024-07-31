from typing import List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.schemas.reservation import ReservationRead
from app.core.exceptions import NotificationNotFoundError, UserNotFoundError
from app.core.config import get_logger
from app.utils.templates import get_notification_template
# from app.utils.email import send_email_async
# from app.utils.sms import send_sms_async
from app.utils.email import send_email_sync
from app.utils.sms import send_sms_sync

logger = get_logger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notification(self, notification_id: int) -> Notification:
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.warning(f"Notification with id {notification_id} not found")
            raise NotificationNotFoundError(f"Notification with id {notification_id} not found")
        return notification

    def get_notifications(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[Notification]:
        query = self.db.query(Notification)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def create_notification(self, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.dict())
        self.db.add(db_notification)
        try:
            self.db.commit()
            self.db.refresh(db_notification)
            logger.info(f"Notification created: {db_notification.id}")
            return db_notification
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise

    def update_notification(self, notification_id: int, notification: NotificationUpdate) -> Notification:
        db_notification = self.get_notification(notification_id)
        update_data = notification.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_notification, key, value)
        try:
            self.db.commit()
            self.db.refresh(db_notification)
            logger.info(f"Notification updated: {notification_id}")
            return db_notification
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification: {str(e)}")
            raise

    def delete_notification(self, notification_id: int):
        db_notification = self.get_notification(notification_id)
        try:
            self.db.delete(db_notification)
            self.db.commit()
            logger.info(f"Notification deleted: {notification_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting notification: {str(e)}")
            raise

    def notify_user(self, user_id: int, title: str, content: str, type: str = "GENERAL") -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundError(f"User with id {user_id} not found")

        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=type
        )
        self.db.add(notification)
        try:
            self.db.commit()
            logger.info(f"Notification created for user {user_id}")

            # 记录要发送的邮件内容
            logger.info(f"Email would be sent to {user.email}: Subject: {title}, Content: {content}")
            logger.info(f"SMS would be sent to {user.phone}: Content: {content}")

            # # 同步发送邮件和短信
            # send_email_sync(user.email, title, content)
            # send_sms_sync(user.phone, content)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error notifying user {user_id}: {str(e)}")
            raise

    def send_reservation_reminder(self, reservation: ReservationRead) -> None:
        user = self.db.query(User).filter(User.id == reservation.user_id).first()
        if user:
            content = get_notification_template("reservation_reminder", {
                "username": user.username,
                "sport_venue_name": reservation.sport_venue_name,
                "venue_name": reservation.venue_name,
                "date": reservation.date,
                "start_time": reservation.start_time,
                "end_time": reservation.end_time
            })
            self.notify_user(
                user_id=user.id,
                title="Reservation Reminder",
                content=content,
                type="REMINDER"
            )
        else:
            logger.warning(f"User not found for reservation reminder: {reservation.user_id}")

    def send_reservation_cancellation_notice(self, reservation: ReservationRead, reason: str) -> None:
        user = self.db.query(User).filter(User.id == reservation.user_id).first()
        if user:
            content = get_notification_template("reservation_cancellation", {
                "username": user.username,
                "sport_venue_name": reservation.sport_venue_name,
                "venue_name": reservation.venue_name,
                "date": reservation.date,
                "start_time": reservation.start_time,
                "end_time": reservation.end_time,
                "reason": reason
            })
            self.notify_user(
                user_id=user.id,
                title="Reservation Cancellation Notice",
                content=content,
                type="CANCELLATION"
            )
        else:
            logger.warning(f"User not found for reservation cancellation notice: {reservation.user_id}")

    def send_bulk_notifications(self, user_ids: List[int], title: str, content: str,
                                      type: str = "GENERAL") -> None:
        for user_id in user_ids:
            try:
                self.notify_user(user_id, title, content, type)
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
