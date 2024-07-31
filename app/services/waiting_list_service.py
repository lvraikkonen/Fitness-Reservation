from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.waiting_list import WaitingList
from app.schemas.waiting_list import WaitingListCreate
from app.models.reservation import Reservation
from app.core.exceptions import WaitingListEntryNotFoundError, WaitingListEntryExistsError


class WaitingListService:
    def __init__(self, db: Session):
        self.db = db

    def get_waiting_list_entry(self, entry_id: int) -> WaitingList:
        entry = self.db.query(WaitingList).filter(WaitingList.id == entry_id).first()
        if not entry:
            raise WaitingListEntryNotFoundError(f"Waiting list entry with id {entry_id} not found")
        return entry

    def get_waiting_list(self, reservation_id: int = None, skip: int = 0, limit: int = 100) -> List[WaitingList]:
        query = self.db.query(WaitingList)
        if reservation_id:
            query = query.filter(WaitingList.reservation_id == reservation_id)
        return query.order_by(WaitingList.created_at).offset(skip).limit(limit).all()

    def create_waiting_list_entry(self, entry: WaitingListCreate) -> WaitingList:
        # 检查用户是否已经在等待列表中
        self._check_existing_entry(entry.user_id, entry.reservation_id)

        db_entry = WaitingList(**entry.dict())
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return db_entry

    def delete_waiting_list_entry(self, entry_id: int):
        db_entry = self.get_waiting_list_entry(entry_id)
        self.db.delete(db_entry)
        self.db.commit()

    def get_next_waiting_user(self, venue_available_time_slot_id: int) -> Optional[WaitingList]:
        return self.db.query(WaitingList).filter(
            WaitingList.venue_available_time_slot_id == venue_available_time_slot_id,
            WaitingList.is_expired == False
        ).order_by(WaitingList.created_at).first()

    def remove_from_waiting_list(self, waiting_list_entry: WaitingList) -> None:
        self.db.delete(waiting_list_entry)
        self.db.flush()  # 使用 flush 而不是 commit，让 ReservationService 控制事务

    def clean_expired_entries(self, expiration_days: int = 7):
        """清理过期的等待列表条目"""
        expiration_date = datetime.utcnow() - timedelta(days=expiration_days)
        expired_entries = self.db.query(WaitingList).filter(WaitingList.created_at < expiration_date).all()
        for entry in expired_entries:
            self.db.delete(entry)
        self.db.commit()

    def _check_existing_entry(self, user_id: int, reservation_id: int):
        """检查用户是否已经在特定预约的等待列表中"""
        existing_entry = self.db.query(WaitingList).filter(
            WaitingList.user_id == user_id,
            WaitingList.reservation_id == reservation_id
        ).first()
        if existing_entry:
            raise WaitingListEntryExistsError("User is already in the waiting list for this reservation")

    def get_waiting_list_stats(self, venue_id: Optional[int] = None, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None):
        """提供等待列表的统计信息"""
        query = self.db.query(
            func.count(WaitingList.id).label("total_entries"),
            func.avg(func.extract('epoch', func.now() - WaitingList.created_at)).label("avg_wait_time")
        )

        if venue_id:
            query = query.join(Reservation).filter(Reservation.venue_id == venue_id)

        if start_date:
            query = query.filter(WaitingList.created_at >= start_date)

        if end_date:
            query = query.filter(WaitingList.created_at <= end_date)

        result = query.first()

        # 获取最受欢迎的时段
        popular_times_query = self.db.query(
            func.date_trunc('hour', Reservation.start_time).label("hour"),
            func.count(WaitingList.id).label("count")
        ).join(Reservation).group_by("hour").order_by(func.count(WaitingList.id).desc()).limit(5)

        popular_times = [{"hour": row.hour, "count": row.count} for row in popular_times_query.all()]

        return {
            "total_entries": result.total_entries,
            "average_wait_time": result.avg_wait_time,
            "popular_times": popular_times
        }

    def check_user_waiting_list_status(self, user_id: int, venue_id: Optional[int] = None):
        """检查用户在等待列表中的状态"""
        query = self.db.query(WaitingList).filter(WaitingList.user_id == user_id)

        if venue_id:
            query = query.join(Reservation).filter(Reservation.venue_id == venue_id)

        waiting_entries = query.all()

        return [
            {
                "entry_id": entry.id,
                "reservation_id": entry.reservation_id,
                "created_at": entry.created_at,
                "position": self._get_waiting_list_position(entry.reservation_id, entry.created_at)
            } for entry in waiting_entries
        ]

    def _get_waiting_list_position(self, reservation_id: int, created_at: datetime) -> int:
        """获取用户在特定预约等待列表中的位置"""
        position = self.db.query(func.count(WaitingList.id)).filter(
            WaitingList.reservation_id == reservation_id,
            WaitingList.created_at < created_at
        ).scalar()
        return position + 1
