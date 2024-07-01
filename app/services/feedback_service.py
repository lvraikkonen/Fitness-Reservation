from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.deps import get_db


class FeedbackService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_feedback(self, feedback_id: int) -> Feedback:
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback

    def get_feedbacks(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[Feedback]:
        query = self.db.query(Feedback)
        if user_id:
            query = query.filter(Feedback.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def create_feedback(self, feedback: FeedbackCreate) -> Feedback:
        db_feedback = Feedback(**feedback.dict())
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def update_feedback(self, feedback_id: int, feedback: FeedbackUpdate) -> Feedback:
        db_feedback = self.get_feedback(feedback_id)
        update_data = feedback.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_feedback, key, value)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def delete_feedback(self, feedback_id: int):
        db_feedback = self.get_feedback(feedback_id)
        self.db.delete(db_feedback)
        self.db.commit()
