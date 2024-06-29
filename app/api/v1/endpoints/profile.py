from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.profile import ProfileResponse, ProfileCreate, ProfileUpdate
from app.services.profile_service import get_profile_by_user_id, create_or_update_profile
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_profile = get_profile_by_user_id(db, current_user.id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


@router.post("/me", response_model=ProfileResponse)
def create_my_profile(profile: ProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_or_update_profile(db, current_user.id, profile)


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(profile: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_profile = get_profile_by_user_id(db, current_user.id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return create_or_update_profile(db, current_user.id, profile)
