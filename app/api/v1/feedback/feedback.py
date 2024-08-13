from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackRead, FeedbackPaginatedResponse
from app.services.feedback_service import FeedbackService
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from typing import Optional
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feedback_data.user_id = current_user.id
    return FeedbackService(db).create_feedback(feedback_data)


@router.get("/", response_model=FeedbackPaginatedResponse)
def get_all_feedbacks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    venue_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    skip = (page - 1) * limit
    feedbacks, total = FeedbackService(db).get_all_feedbacks(skip, limit, venue_id, user_id)
    return FeedbackPaginatedResponse(
        items=feedbacks,
        total=total,
        page=page,
        size=limit
    )


@router.get("/my", response_model=FeedbackPaginatedResponse)
def get_user_feedbacks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * limit
    feedbacks, total = FeedbackService(db).get_user_feedbacks(current_user.id, skip, limit)
    return FeedbackPaginatedResponse(
        items=feedbacks,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{feedback_id}", response_model=FeedbackRead)
def get_feedback(
    feedback_id: int = Path(..., title="The ID of the feedback to get"),
    db: Session = Depends(get_db)
):
    return FeedbackService(db).get_feedback_by_id(feedback_id)


@router.put("/{feedback_id}", response_model=FeedbackRead)
def update_feedback(
    feedback_id: int = Path(..., title="The ID of the feedback to update"),
    feedback_data: FeedbackUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_feedback = FeedbackService(db).get_feedback_by_id(feedback_id)
    if existing_feedback.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this feedback")
    return FeedbackService(db).update_feedback(feedback_id, feedback_data)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int = Path(..., title="The ID of the feedback to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_feedback = FeedbackService(db).get_feedback_by_id(feedback_id)
    if existing_feedback.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this feedback")
    FeedbackService(db).delete_feedback(feedback_id)
    return {"detail": "Feedback deleted successfully"}


@router.post("/{feedback_id}/reply", response_model=FeedbackRead)
def reply_to_feedback(
    feedback_id: int = Path(..., title="The ID of the feedback to reply to"),
    reply: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can reply to feedback")
    return FeedbackService(db).reply_to_feedback(feedback_id, reply)
