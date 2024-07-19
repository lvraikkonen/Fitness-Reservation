from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.deps import get_db
from app.core.exceptions import ValidationError, FeedbackNotFoundError
from app.core.config import get_logger

logger = get_logger(__name__)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(self, feedback_data: FeedbackCreate):
        try:
            self._validate_feedback_data(feedback_data)
            feedback = Feedback(**feedback_data.dict())
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Feedback created: ID {feedback.id}")
            return feedback
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating feedback: {str(e)}")
            raise

    def get_feedback_by_id(self, feedback_id: int) -> Feedback:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            logger.warning(f"Feedback not found: ID {feedback_id}")
            raise FeedbackNotFoundError(f"Feedback with id {feedback_id} not found")
        return feedback

    def get_all_feedbacks(self, skip: int = 0, limit: int = 100, venue_id: Optional[int] = None) -> List[Feedback]:
        query = self.db.query(Feedback)
        if venue_id:
            query = query.filter(Feedback.venue_id == venue_id)
        return query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()

    def update_feedback(self, feedback_id: int, feedback_data: FeedbackUpdate) -> Feedback:
        feedback = self.get_feedback_by_id(feedback_id)
        try:
            for field, value in feedback_data.dict(exclude_unset=True).items():
                setattr(feedback, field, value)
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Feedback updated: ID {feedback_id}")
            return feedback
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating feedback: {str(e)}")
            raise

    def delete_feedback(self, feedback_id: int) -> None:
        feedback = self.get_feedback_by_id(feedback_id)
        try:
            self.db.delete(feedback)
            self.db.commit()
            logger.info(f"Feedback deleted: ID {feedback_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting feedback: {str(e)}")
            raise

    def reply_to_feedback(self, feedback_id: int, reply: str) -> Feedback:
        feedback = self.get_feedback_by_id(feedback_id)
        try:
            feedback.reply = reply
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Reply added to feedback: ID {feedback_id}")
            return feedback
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
