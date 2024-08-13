from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.feedback import Feedback
from app.models.user import User
from app.models.venue import Venue
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackRead
from app.core.exceptions import ValidationError, FeedbackNotFoundError
from app.core.config import get_logger

logger = get_logger(__name__)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(self, feedback_data: FeedbackCreate) -> FeedbackRead:
        try:
            self._validate_feedback_data(feedback_data)
            feedback = Feedback(**feedback_data.dict())
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Feedback created: ID {feedback.id}")
            return self._feedback_to_read(feedback)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating feedback: {str(e)}")
            raise

    def get_feedback_by_id(self, feedback_id: int) -> FeedbackRead:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            logger.warning(f"Feedback not found: ID {feedback_id}")
            raise FeedbackNotFoundError(f"Feedback with id {feedback_id} not found")
        return self._feedback_to_read(feedback)

    def get_all_feedbacks(
            self,
            skip: int = 0,
            limit: int = 10,
            venue_id: Optional[int] = None,
            user_id: Optional[int] = None
    ) -> Tuple[List[FeedbackRead], int]:
        query = self.db.query(Feedback)

        if venue_id:
            query = query.filter(Feedback.venue_id == venue_id)
        if user_id:
            query = query.filter(Feedback.user_id == user_id)

        total = query.count()
        feedbacks = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()

        return [self._feedback_to_read(feedback) for feedback in feedbacks], total

    def get_user_feedbacks(
            self,
            user_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> Tuple[List[FeedbackRead], int]:
        query = self.db.query(Feedback).filter(Feedback.user_id == user_id)
        total = query.count()
        feedbacks = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()

        return [self._feedback_to_read(feedback) for feedback in feedbacks], total

    def update_feedback(self, feedback_id: int, feedback_data: FeedbackUpdate) -> FeedbackRead:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise FeedbackNotFoundError(f"Feedback with id {feedback_id} not found")
        try:
            for field, value in feedback_data.dict(exclude_unset=True).items():
                setattr(feedback, field, value)
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Feedback updated: ID {feedback_id}")
            return self._feedback_to_read(feedback)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating feedback: {str(e)}")
            raise

    def delete_feedback(self, feedback_id: int) -> None:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise FeedbackNotFoundError(f"Feedback with id {feedback_id} not found")
        try:
            self.db.delete(feedback)
            self.db.commit()
            logger.info(f"Feedback deleted: ID {feedback_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting feedback: {str(e)}")
            raise

    def reply_to_feedback(self, feedback_id: int, reply: str) -> FeedbackRead:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise FeedbackNotFoundError(f"Feedback with id {feedback_id} not found")
        try:
            feedback.reply = reply
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Reply added to feedback: ID {feedback_id}")
            return self._feedback_to_read(feedback)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error replying to feedback: {str(e)}")
            raise

    def get_venue_rating(self, venue_id: int) -> float:
        result = self.db.query(func.avg(Feedback.rating)).filter(Feedback.venue_id == venue_id).scalar()
        return round(result, 2) if result else 0.0

    def _validate_feedback_data(self, feedback_data: FeedbackCreate) -> None:
        if feedback_data.rating < 1 or feedback_data.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
        if len(feedback_data.content) < 5:
            raise ValidationError("Feedback content must be at least 5 characters long")

    def _feedback_to_read(self, feedback: Feedback) -> FeedbackRead:
        user = self.db.query(User).filter(User.id == feedback.user_id).first()
        venue = self.db.query(Venue).filter(Venue.id == feedback.venue_id).first()
        return FeedbackRead(
            id=feedback.id,
            user_id=feedback.user_id,
            venue_id=feedback.venue_id,
            title=feedback.title,
            content=feedback.content,
            rating=feedback.rating,
            reply=feedback.reply,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            user_name=user.username if user else "Unknown User",
            venue_name=venue.name if venue else "Unknown Venue"
        )
