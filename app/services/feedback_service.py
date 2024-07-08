from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.deps import get_db


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(self, feedback_data: FeedbackCreate):
        feedback = Feedback(**feedback_data.dict())
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_feedback_by_id(self, feedback_id: int):
        return self.db.query(Feedback).filter(Feedback.id == feedback_id).first()

    def get_all_feedbacks(self):
        return self.db.query(Feedback).all()

    def update_feedback(self, feedback_id: int, feedback_data: FeedbackUpdate):
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            for field, value in feedback_data.dict(exclude_unset=True).items():
                setattr(feedback, field, value)
            self.db.commit()
            self.db.refresh(feedback)
        return feedback

    def delete_feedback(self, feedback_id: int):
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            self.db.delete(feedback)
            self.db.commit()
        return feedback

    def reply_to_feedback(self, feedback_id: int, reply: str):
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            feedback.reply = reply
            self.db.commit()
            self.db.refresh(feedback)
        return feedback
