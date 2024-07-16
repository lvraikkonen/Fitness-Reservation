from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.sport_venue import SportVenue
from app.models.venue import Venue, VenueStatus
from app.models.facility import Facility
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.reservation import Reservation, ReservationStatus
from app.models.waiting_list import WaitingList
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.core.security import get_password_hash
from datetime import date, time, datetime, timedelta
from app.core.config import get_logger

logger = get_logger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)


def recreate_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_sample_data():
    with SessionLocal() as db:
        # 创建示例用户
        user1 = User(username="claus", email="claus@example.com", password=get_password_hash("123456"), phone="123456", role=0, is_leader=False)
        user2 = User(username="kimi", email="kimi@example.com", password=get_password_hash("123456"), phone="123456", role=0, is_leader=False)
        user3 = User(username="Elon", email="elonmusk@example.com", password=get_password_hash("123456"), phone="123456", role=0, is_leader=True)
        admin = User(username="Admin", email="admin@example.com", password=get_password_hash("123456"),
                     phone="123456", role=1, is_leader=False)

        db.add_all([user1, user2, user3, admin])
        db.commit()

        # 创建示例运动场馆
        sport_venue1 = SportVenue(name="Basketball Court", location="Building A")
        sport_venue2 = SportVenue(name="Tennis Court", location="Building B")
        db.add_all([sport_venue1, sport_venue2])
        db.commit()

        # 创建示例具体场馆
        venue1 = Venue(sport_venue_id=sport_venue1.id, name="Court 1", capacity=10, default_capacity=8,
                       status=VenueStatus.OPEN)
        venue2 = Venue(sport_venue_id=sport_venue1.id, name="Court 2", capacity=12, default_capacity=10,
                       status=VenueStatus.OPEN)
        venue3 = Venue(sport_venue_id=sport_venue2.id, name="Court 3", capacity=8, default_capacity=6,
                       status=VenueStatus.MAINTENANCE)
        db.add_all([venue1, venue2, venue3])
        db.commit()

        # 创建场馆设施
        facility1 = Facility(venue_id=venue1.id, name="Locker Room", description="Locker room for Court 1")
        facility2 = Facility(venue_id=venue2.id, name="Shower Room", description="Shower room for Court 2")
        facility3 = Facility(venue_id=venue1.id, name="Shower Room", description="Shower room for Court 1")
        db.add_all([facility1, facility2, facility3])
        db.commit()

        # 创建未来14天的 VenueAvailableTimeSlot
        today = datetime.now().date()
        for venue in [venue1, venue2, venue3]:
            for day in range(14):
                current_date = today + timedelta(days=day)
                for hour in range(7, 22):  # 假设开放时间是 7:00 到 22:00
                    start_time = time(hour, 0)
                    end_time = time(hour + 1, 0)
                    available_slot = VenueAvailableTimeSlot(
                        venue_id=venue.id,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        capacity=venue.default_capacity
                    )
                    db.add(available_slot)
        db.commit()

        # 创建预约时间段（保持原有的示例数据）
        time_slot1 = ReservationTimeSlot(venue_id=venue1.id, date=date(2024, 7, 1), start_time=time(9, 0),
                                         end_time=time(10, 0))
        time_slot2 = ReservationTimeSlot(venue_id=venue1.id, date=date(2024, 7, 1), start_time=time(10, 0),
                                         end_time=time(11, 0))
        time_slot3 = ReservationTimeSlot(venue_id=venue2.id, date=date(2024, 7, 2), start_time=time(14, 0),
                                         end_time=time(15, 0))
        db.add_all([time_slot1, time_slot2, time_slot3])
        db.commit()

        # 创建预约
        reservation1 = Reservation(user_id=user1.id, time_slot_id=time_slot1.id, status=ReservationStatus.CONFIRMED)
        reservation2 = Reservation(user_id=user2.id, time_slot_id=time_slot2.id, status=ReservationStatus.PENDING)
        db.add_all([reservation1, reservation2])
        db.commit()

        # 创建反馈
        feedback1 = Feedback(user=user1, venue=venue1, title="Great facilities", rating=5,
                             content="The facilities at the basketball court are amazing!")
        feedback2 = Feedback(user=user2, venue=venue2, title="Suggestion", rating=3,
                             content="It would be great to have more time slots available.")
        db.add_all([feedback1, feedback2])
        db.commit()

        # 创建通知
        notification1 = Notification(user_id=user1.id, title="Reservation confirmed",
                                     content="Your reservation for Court 1 has been confirmed.", type="reservation")
        notification2 = Notification(user_id=user2.id, title="New time slot available",
                                     content="A new time slot for Court 2 is now available.", type="time_slot")
        db.add_all([notification1, notification2])
        db.commit()

        # 创建领导预留时间
        leader_reserved_time1 = LeaderReservedTime(user_id=user3.id, venue_id=venue1.id, day_of_week=1,
                                                   start_time=time(13, 0), end_time=time(14, 0))
        leader_reserved_time2 = LeaderReservedTime(user_id=user3.id, venue_id=venue2.id, day_of_week=3,
                                                   start_time=time(16, 0), end_time=time(17, 0))
        db.add_all([leader_reserved_time1, leader_reserved_time2])
        db.commit()

        logger.info("Sample data created successfully.")


if __name__ == "__main__":
    init_db()
    create_sample_data()
    logger.info("Database initialized with sample data.")
