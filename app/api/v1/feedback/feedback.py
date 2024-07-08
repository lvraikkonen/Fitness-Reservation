from fastapi import APIRouter, Depends
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, Feedback
from app.services.feedback_service import FeedbackService
from sqlalchemy.orm import Session
from app.deps import get_db
from typing import List

router = APIRouter()


@router.post("/", response_model=Feedback)
def create_feedback(feedback_data: FeedbackCreate, db: Session = Depends(get_db)):
    return FeedbackService(db).create_feedback(feedback_data)


@router.get("/{feedback_id}", response_model=Feedback)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    return FeedbackService(db).get_feedback_by_id(feedback_id)


@router.get("/", response_model=List[Feedback])
def get_all_feedbacks(db: Session = Depends(get_db)):
    return FeedbackService(db).get_all_feedbacks()


@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(feedback_id: int, feedback_data: FeedbackUpdate, db: Session = Depends(get_db)):
    return FeedbackService(db).update_feedback(feedback_id, feedback_data)


@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    return FeedbackService(db).delete_feedback(feedback_id)


@router.post("/{feedback_id}/reply")
def reply_to_feedback(feedback_id: int, reply: str, db: Session = Depends(get_db)):
    return FeedbackService(db).reply_to_feedback(feedback_id, reply)
