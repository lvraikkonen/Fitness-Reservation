from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def get_profile_by_user_id(db: Session, user_id: int):
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_or_update_profile(db: Session, user_id: int, profile: ProfileCreate):
    db_profile = get_profile_by_user_id(db, user_id)
    if db_profile:
        update_profile(db, db_profile, profile)
    else:
        db_profile = create_profile(db, user_id, profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def create_profile(db: Session, user_id: int, profile: ProfileCreate):
    db_profile = Profile(**profile.dict(), user_id=user_id)
    db.add(db_profile)
    return db_profile


def update_profile(db: Session, db_profile: Profile, profile: ProfileUpdate):
    update_data = profile.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
