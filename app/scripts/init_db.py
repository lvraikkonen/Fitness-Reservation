from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.core.security import get_password_hash


def init_db():
    Base.metadata.create_all(bind=engine)


def recreate_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_sample_data():
    db = SessionLocal()
    # 创建样例用户
    user1 = User(
        username="admin",
        email="admin@example.com",
        password=get_password_hash("123456"),
        is_staff=True,
        is_active=True,
    )
    user2 = User(
        username="claus",
        email="claus@example.com",
        password=get_password_hash("123456"),
        is_staff=True,
        is_active=True,
    )
    db.add_all([user1, user2])
    db.commit()

    # 创建样例用户资料
    profile1 = Profile(
        user_id=user1.id,
        full_name="John Doe",
        department="IT",
        contact_info="123-456-7890",
        preferred_sports="Basketball, Soccer",
        preferred_time="Weekends",
    )
    profile2 = Profile(
        user_id=user2.id,
        full_name="Jane Doe",
        department="HR",
        contact_info="987-654-3210",
        preferred_sports="Yoga, Running",
        preferred_time="Weekdays",
    )
    db.add_all([profile1, profile2])
    db.commit()


def main():
    init_db()
    with Session(engine) as db:
        create_sample_data(db)


if __name__ == "__main__":
    main()
