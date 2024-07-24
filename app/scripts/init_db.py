from app.db.database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.sport_venue import SportVenue
from app.models.venue import Venue, VenueStatus
from app.models.facility import Facility
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_rules import ReservationRules
from app.models.waiting_list import WaitingList
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.core.security import get_password_hash
from datetime import date, time, datetime, timedelta
from app.core.config import get_logger
import random

logger = get_logger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)


def recreate_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_sample_data():
    with SessionLocal() as db:
        # 创建用户
        create_sample_users(db)

        # 创建运动场馆
        create_sample_sport_venues(db)

        # 创建具体场馆
        create_sample_venues(db)

        # 创建场馆设施
        create_sample_facilities(db)

        # 创建预约规则
        create_sample_reservation_rules(db)

        # 创建可用时间段
        create_sample_available_time_slots(db)

        create_sample_reservations(db)
        create_sample_feedbacks(db)
        create_sample_leader_reserved_times(db)
        create_sample_notifications(db)
        create_sample_waiting_lists(db)

        logger.info("Sample data created successfully.")


def create_sample_users(db: Session):
    users = [
        User(username="admin", email="admin@example.com", password=get_password_hash("123456"),
             phone="1234567890", role=UserRole.ADMIN, is_leader=True, full_name="Admin User",
             department="IT"),
        User(username="claus", email="claus@example.com", password=get_password_hash("123456"),
             phone="1234567891", role=UserRole.EMPLOYEE, full_name="Claus Lv",
             department="HR"),
        User(username="shuo", email="shuo-vip@example.com", password=get_password_hash("123456"),
             phone="1234567892", role=UserRole.VIP, full_name="Shuo Lv",
             department="BizOps-Dev"),
        User(username="Elon", email="elonmusk@example.com", password=get_password_hash("123456"),
             phone="123456", role=UserRole.VIP, is_leader=True),
    ]

    db.add_all(users)
    db.commit()


def create_sample_sport_venues(db: Session):
    sport_venues = [
        SportVenue(name="Main Gym", location="Building A"),
        SportVenue(name="Outdoor Field", location="Behind Building B"),
    ]
    db.add_all(sport_venues)
    db.commit()


def create_sample_venues(db: Session):
    venues = [
        Venue(sport_venue_id=1, name="Basketball Court", capacity=20, default_capacity=20,
              status=VenueStatus.OPEN, notice="Please wear appropriate footwear."),
        Venue(sport_venue_id=1, name="Yoga Room", capacity=15, default_capacity=15,
              status=VenueStatus.OPEN, notice="Yoga mats are provided."),
        Venue(sport_venue_id=2, name="Soccer Field", capacity=30, default_capacity=30,
              status=VenueStatus.OPEN, notice="No metal cleats allowed."),
    ]
    db.add_all(venues)
    db.commit()


def create_sample_facilities(db: Session):
    facilities = [
        Facility(venue_id=1, name="Basketball Hoop", description="Regulation height basketball hoop"),
        Facility(venue_id=2, name="Yoga Mat", description="20 yoga mats available"),
        Facility(venue_id=3, name="Goal Post", description="Two regulation size soccer goal posts"),
    ]
    db.add_all(facilities)
    db.commit()


def create_sample_reservation_rules(db: Session):
    venues = db.query(Venue).all()

    for venue in venues:
        # 为每个场馆创建员工规则
        employee_rule = ReservationRules(
            venue_id=venue.id,
            user_role=UserRole.EMPLOYEE,
            min_duration=timedelta(hours=1),
            max_duration=timedelta(hours=2),
            max_daily_reservations=2,
            max_weekly_reservations=4,
            max_monthly_reservations=10
        )

        # 为每个场馆创建VIP规则
        vip_rule = ReservationRules(
            venue_id=venue.id,
            user_role=UserRole.VIP,
            min_duration=timedelta(hours=1),
            max_duration=timedelta(hours=3),
            max_daily_reservations=4,
            max_weekly_reservations=6,
            max_monthly_reservations=20
        )

        db.add_all([employee_rule, vip_rule])

    db.commit()
    print(f"Created reservation rules for {len(venues)} venues.")


def create_sample_available_time_slots(db: Session):
    today = datetime.now().date()
    time_slots = []
    for i in range(7):  # 创建未来7天的时间段
        date_key = today + timedelta(days=i)
        time_slots.extend([
            VenueAvailableTimeSlot(venue_id=1, date=date_key, start_time=time(9, 0), end_time=time(11, 0), capacity=20),
            VenueAvailableTimeSlot(venue_id=1, date=date_key, start_time=time(13, 0), end_time=time(15, 0), capacity=20),
            VenueAvailableTimeSlot(venue_id=2, date=date_key, start_time=time(10, 0), end_time=time(11, 0), capacity=15),
            VenueAvailableTimeSlot(venue_id=2, date=date_key, start_time=time(14, 0), end_time=time(15, 0), capacity=15),
            VenueAvailableTimeSlot(venue_id=3, date=date_key, start_time=time(15, 0), end_time=time(17, 0), capacity=30),
        ])
    db.add_all(time_slots)
    db.commit()


def create_sample_reservations(db: Session):
    users = db.query(User).all()
    time_slots = db.query(VenueAvailableTimeSlot).all()

    reservations = []
    for _ in range(10):  # 创建10个预约
        user = random.choice(users)
        time_slot = random.choice(time_slots)
        status = random.choice(list(ReservationStatus))

        reservation = Reservation(
            user_id=user.id,
            venue_id=time_slot.venue_id,
            venue_available_time_slot_id=time_slot.id,
            status=status,
            is_recurring=False
        )
        reservations.append(reservation)

    db.add_all(reservations)
    db.commit()


def create_sample_feedbacks(db: Session):
    users = db.query(User).all()
    venues = db.query(Venue).all()

    feedbacks = []
    for _ in range(5):  # 创建5个反馈
        user = random.choice(users)
        venue = random.choice(venues)

        feedback = Feedback(
            user_id=user.id,
            venue_id=venue.id,
            title=f"Feedback for {venue.name}",
            content=f"This is a sample feedback for {venue.name}.",
            rating=random.randint(1, 5)
        )
        feedbacks.append(feedback)

    db.add_all(feedbacks)
    db.commit()


def create_sample_leader_reserved_times(db: Session):
    leaders = db.query(User).filter(User.is_leader == True).all()
    venues = db.query(Venue).all()

    reserved_times = []
    for leader in leaders:
        venue = random.choice(venues)

        reserved_time = LeaderReservedTime(
            user_id=leader.id,
            venue_id=venue.id,
            day_of_week=random.randint(0, 6),
            start_time=time(hour=random.randint(9, 17)),
            end_time=time(hour=random.randint(18, 21))
        )
        reserved_times.append(reserved_time)

    db.add_all(reserved_times)
    db.commit()


def create_sample_notifications(db: Session):
    users = db.query(User).all()

    notifications = []
    for user in users:
        notification = Notification(
            user_id=user.id,
            title="Welcome to the Fitness Reservation System",
            content="Thank you for joining our fitness reservation system. Enjoy your workouts!",
            type="welcome",
            is_read=False
        )
        notifications.append(notification)

    db.add_all(notifications)
    db.commit()


def create_sample_waiting_lists(db: Session):
    users = db.query(User).all()
    reservations = db.query(Reservation).all()

    waiting_lists = []
    for _ in range(5):  # 创建5个等候记录
        user = random.choice(users)
        reservation = random.choice(reservations)

        waiting_list = WaitingList(
            reservation_id=reservation.id,
            user_id=user.id,
            is_expired=False
        )
        waiting_lists.append(waiting_list)

    db.add_all(waiting_lists)
    db.commit()


if __name__ == "__main__":
    init_db()
    create_sample_data()
    logger.info("Database initialized with sample data.")
