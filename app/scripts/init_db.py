from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.sport_venue import SportVenue
from app.models.venue import Venue
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.reservation import Reservation, ReservationStatus
from app.models.waiting_list import WaitingList
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.feedback import Feedback
from app.models.notification import Notification


def init_db():
    Base.metadata.create_all(bind=engine)


def recreate_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_sample_data():
    with SessionLocal() as db:
        # 创建示例用户
        user1 = User(username="john", email="john@example.com", hashed_password="hashed_password")
        user2 = User(username="jane", email="jane@example.com", hashed_password="hashed_password")
        db.add_all([user1, user2])
        db.commit()

        # 创建示例运动场馆
        sport_venue1 = SportVenue(name="Basketball Court", location="1st Floor")
        sport_venue2 = SportVenue(name="Badminton Court", location="2nd Floor")
        db.add_all([sport_venue1, sport_venue2])
        db.commit()

        # 创建示例具体场馆
        venue1 = Venue(sport_venue_id=sport_venue1.id, name="Court A", capacity=10)
        venue2 = Venue(sport_venue_id=sport_venue2.id, name="Court B", capacity=8)
        db.add_all([venue1, venue2])
        db.commit()

        # 创建示例预约时间段
        time_slot1 = ReservationTimeSlot(venue_id=venue1.id, start_time="09:00", end_time="10:00")
        time_slot2 = ReservationTimeSlot(venue_id=venue2.id, start_time="14:00", end_time="15:00")
        db.add_all([time_slot1, time_slot2])
        db.commit()

        # 创建示例预约
        reservation1 = Reservation(user_id=user1.id, time_slot_id=time_slot1.id, status=ReservationStatus.CONFIRMED)
        reservation2 = Reservation(user_id=user2.id, time_slot_id=time_slot2.id, status=ReservationStatus.PENDING)
        db.add_all([reservation1, reservation2])
        db.commit()

        # 创建示例等候列表
        waiting_list1 = WaitingList(reservation_id=reservation1.id, user_id=user2.id)
        db.add(waiting_list1)
        db.commit()

        # 创建示例领导预留时间
        leader_reserved_time1 = LeaderReservedTime(user_id=user1.id, venue_id=venue1.id, start_time="13:00", end_time="14:00")
        db.add(leader_reserved_time1)
        db.commit()

        # 创建示例反馈
        feedback1 = Feedback(user_id=user1.id, title="Great service", content="The staff were very helpful.")
        db.add(feedback1)
        db.commit()

        # 创建示例通知
        notification1 = Notification(user_id=user1.id, title="Reservation confirmed", content="Your reservation has been confirmed.")
        db.add(notification1)
        db.commit()


def main():
    init_db()
    create_sample_data()


if __name__ == "__main__":
    main()
