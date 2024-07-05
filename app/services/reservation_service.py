from typing import List, Union, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, date

from app.models.venue import Venue
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.waiting_list import WaitingList
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationTimeSlotRead, ReservationRead
from app.schemas.reservation_time_slot import ReservationTimeSlotBase
from app.schemas.waiting_list import WaitingListReadWithReservationTimeSlot

from app.services.notification_service import NotificationService


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db=self.db)

    def get_reservations(self, user_id: int):
        return self.db.query(Reservation).filter(Reservation.user_id == user_id).all()

    def get_reservation(self, reservation_id: int):
        return self.db.query(Reservation).filter(Reservation.id == reservation_id).first()

    def update_reservation(self, reservation_id: int, reservation: ReservationUpdate):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            update_data = reservation.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reservation, key, value)
            self.db.commit()
            self.db.refresh(db_reservation)
        return db_reservation

    def delete_reservation(self, reservation_id: int):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            self.db.delete(db_reservation)
            self.db.commit()
        return db_reservation

    def get_venue_calendar(
            self,
            venue_id: int,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            page: int = 1,
            page_size: int = 10
    ) -> Dict[str, Any]:
        # 构建查询对象
        query = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id
        )

        # 添加日期范围过滤
        if start_date:
            query = query.filter(ReservationTimeSlot.date >= start_date)
        if end_date:
            query = query.filter(ReservationTimeSlot.date <= end_date)

        # 添加分页功能
        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        reservation_time_slots = query.offset(offset).limit(page_size).all()

        # 将预约时段按照日期分组
        calendar_data: Dict[date, List[ReservationTimeSlotRead]] = {}
        for time_slot in reservation_time_slots:
            reservation_time_slot_read = ReservationTimeSlotRead(
                id=time_slot.id,
                venue_id=time_slot.venue_id,
                date=time_slot.date,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time,
                reservations=[
                    ReservationRead(
                        id=reservation.id,
                        user_id=reservation.user_id,
                        time_slot_id=reservation.time_slot_id,
                        status=reservation.status
                    )
                    for reservation in time_slot.reservations
                ]
            )

            if time_slot.date not in calendar_data:
                calendar_data[time_slot.date] = []
            calendar_data[time_slot.date].append(reservation_time_slot_read)

        return {
            "calendar_data": calendar_data,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size
        }

    def check_reservation_conflict(self, venue_id: int, reservation_data: ReservationTimeSlotBase) -> bool:
        # 检查给定的预约时段是否与现有的预约存在冲突
        conflicting_reservations = self.db.query(Reservation).join(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id,
            ReservationTimeSlot.date == reservation_data.date,
            ReservationTimeSlot.start_time < reservation_data.end_time,
            ReservationTimeSlot.end_time > reservation_data.start_time,
            Reservation.status != ReservationStatus.CANCELLED
        ).count()

        # 获取场馆的容量
        venue_capacity = self.db.query(Venue).filter(Venue.id == venue_id).first().capacity

        # 检查预约时段的可用名额数量
        available_slots = venue_capacity - conflicting_reservations

        # 如果没有可用名额,则存在冲突
        if available_slots <= 0:
            return True

        # 检查给定的预约时段是否与领导预留时间存在冲突
        conflicting_leader_reserved_time = self.db.query(LeaderReservedTime).filter(
            LeaderReservedTime.venue_id == venue_id,
            LeaderReservedTime.day_of_week == reservation_data.date.weekday(),
            LeaderReservedTime.start_time < reservation_data.end_time,
            LeaderReservedTime.end_time > reservation_data.start_time
        ).first()

        # 如果与领导预留时间存在冲突,则存在冲突
        if conflicting_leader_reserved_time:
            return True

        # 如果没有冲突,则不存在冲突
        return False

    # 创建预约
    def create_reservation(self, reservation_data: ReservationCreate) -> Union[Reservation, WaitingList]:
        # 创建 ReservationTimeSlotBase 对象
        time_slot_data = ReservationTimeSlotBase(
            date=reservation_data.date,
            start_time=reservation_data.start_time,
            end_time=reservation_data.end_time
        )

        # 检查预约时段是否存在冲突
        conflict = self.check_reservation_conflict(reservation_data.venue_id, time_slot_data)

        # 查找预约时段
        reservation_time_slot = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == reservation_data.venue_id,
            ReservationTimeSlot.date == reservation_data.date,
            ReservationTimeSlot.start_time == reservation_data.start_time,
            ReservationTimeSlot.end_time == reservation_data.end_time
        ).first()

        # 如果预约时段不存在,则创建一个新的预约时段
        if not reservation_time_slot:
            reservation_time_slot = ReservationTimeSlot(
                venue_id=reservation_data.venue_id,
                date=reservation_data.date,
                start_time=reservation_data.start_time,
                end_time=reservation_data.end_time
            )
            self.db.add(reservation_time_slot)
            self.db.flush()  # 执行插入操作,获取新创建的预约时段的 ID

        if conflict:
            # 如果存在冲突,将用户加入等待列表
            waiting_list_item = self.join_waiting_list(
                venue_id=reservation_data.venue_id,
                reservation_data=time_slot_data,
                user_id=reservation_data.user_id
            )
            return waiting_list_item
        else:
            # 如果没有冲突且有可用名额,创建新的预约记录
            new_reservation = Reservation(
                user_id=reservation_data.user_id,
                time_slot_id=reservation_time_slot.id,
                status=ReservationStatus.PENDING
            )
            self.db.add(new_reservation)
            self.db.commit()
            self.db.refresh(new_reservation)
            return new_reservation

    # 取消预约
    def cancel_reservation(self, reservation_id: int) -> None:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")

        # 将预约状态更新为已取消
        reservation.status = ReservationStatus.CANCELLED
        self.db.commit()

        # 获取预约时段的等待列表
        waiting_list = self.db.query(WaitingList).filter(
            WaitingList.reservation_id == reservation.time_slot_id).order_by(WaitingList.created_at).all()

        if waiting_list:
            # 如果等待列表不为空,将第一个等待的用户分配到预约
            waiting_user = waiting_list[0]
            new_reservation = Reservation(
                user_id=waiting_user.user_id,
                time_slot_id=reservation.time_slot_id,
                status=ReservationStatus.PENDING
            )
            self.db.add(new_reservation)
            self.db.delete(waiting_user)
            self.db.commit()

            # 通知新分配的用户他们的预约现在可用
            self.notification_service.notify_user(waiting_user.user_id, "Your reservation is now available!")

        # 通知原预约用户预约已取消
        self.notification_service.notify_user(reservation.user_id, "Your reservation has been cancelled.")

    # 加入预约等候列表
    def join_waiting_list(self, venue_id: int, reservation_data: ReservationTimeSlotBase, user_id: int) -> WaitingList:
        # 查找预约时段
        reservation_time_slot = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id,
            ReservationTimeSlot.date == reservation_data.date,
            ReservationTimeSlot.start_time == reservation_data.start_time,
            ReservationTimeSlot.end_time == reservation_data.end_time
        ).first()

        # 如果预约时段不存在,则创建一个新的预约时段
        if not reservation_time_slot:
            reservation_time_slot = ReservationTimeSlot(
                venue_id=venue_id,
                date=reservation_data.date,
                start_time=reservation_data.start_time,
                end_time=reservation_data.end_time
            )
            self.db.add(reservation_time_slot)
            self.db.flush()  # 执行插入操作,获取新创建的预约时段的 ID

        # 检查用户是否已经在该预约时段的等待列表中
        existing_waiting_list_item = self.db.query(WaitingList).filter(
            WaitingList.reservation_id == reservation_time_slot.id,
            WaitingList.user_id == user_id
        ).first()

        if existing_waiting_list_item:
            # 如果用户已经在等待列表中,直接返回现有的等待列表对象
            return existing_waiting_list_item
        else:
            # 如果用户不在等待列表中,将用户加入等待列表
            waiting_list_item = WaitingList(
                reservation_id=reservation_time_slot.id,
                user_id=user_id
            )
            self.db.add(waiting_list_item)
            self.db.commit()
            self.db.refresh(waiting_list_item)
            return waiting_list_item

    # 查看预约等候列表
    def get_waiting_list(self, venue_id: int) -> List[WaitingListReadWithReservationTimeSlot]:
        # 查询指定场馆的所有等候列表记录,并按照创建时间排序
        waiting_list_records = self.db.query(WaitingList).join(Reservation).join(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id
        ).order_by(WaitingList.created_at).all()

        # 将等候列表记录转换为 WaitingListReadWithReservationTimeSlot 对象
        waiting_list_read_objects = []
        for waiting_list_record in waiting_list_records:
            reservation_time_slot = waiting_list_record.reservation.time_slot
            waiting_list_read_object = WaitingListReadWithReservationTimeSlot(
                id=waiting_list_record.id,
                user_id=waiting_list_record.user_id,
                reservation_id=waiting_list_record.reservation_id,
                reservation_time_slot=ReservationTimeSlotRead(
                    id=reservation_time_slot.id,
                    venue_id=reservation_time_slot.venue_id,
                    date=reservation_time_slot.date,
                    start_time=reservation_time_slot.start_time,
                    end_time=reservation_time_slot.end_time
                ),
                created_at=waiting_list_record.created_at,
                updated_at=waiting_list_record.updated_at
            )
            waiting_list_read_objects.append(waiting_list_read_object)

        return waiting_list_read_objects

    # 处理等待列表并自动分配预约
    def process_waiting_list(self, reservation_time_slot_id: int) -> None:
        # 获取预约时段的等待列表
        waiting_list = self.db.query(WaitingList).filter(
            WaitingList.reservation_id == reservation_time_slot_id).order_by(WaitingList.created_at).all()

        # 获取预约时段的可用名额
        available_slots = self.db.query(Reservation).filter(
            Reservation.time_slot_id == reservation_time_slot_id,
            Reservation.status != ReservationStatus.CANCELLED
        ).count()
        total_slots = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.id == reservation_time_slot_id).first().venue.capacity

        available_slots = total_slots - available_slots

        # 根据可用名额分配预约给等待列表中的用户
        for _ in range(available_slots):
            if waiting_list:
                waiting_user = waiting_list.pop(0)
                new_reservation = Reservation(
                    user_id=waiting_user.user_id,
                    time_slot_id=reservation_time_slot_id,
                    status=ReservationStatus.PENDING
                )
                self.db.add(new_reservation)
                self.db.delete(waiting_user)
                self.db.commit()

                # 通知新分配的用户他们的预约现在可用
                self.notification_service.notify_user(waiting_user.user_id, "Your reservation is now available!")

    def send_reservation_reminder(self) -> None:
        # 获取当前时间
        current_time = datetime.now()

        # 计算提醒时间范围
        reminder_start_time = current_time + timedelta(hours=1)  # 提前1小时提醒
        reminder_end_time = current_time + timedelta(hours=24)  # 提前24小时提醒

        # 查询在提醒时间范围内且状态为 CONFIRMED 的预约
        reservations = self.db.query(Reservation).join(ReservationTimeSlot).filter(
            Reservation.status == ReservationStatus.CONFIRMED,
            ReservationTimeSlot.start_time >= reminder_start_time,
            ReservationTimeSlot.start_time < reminder_end_time
        ).all()

        # 实例化通知服务
        notification_service = NotificationService()

        # 发送预约提醒
        for reservation in reservations:
            reservation_read = ReservationRead(
                id=reservation.id,
                user_id=reservation.user_id,
                time_slot_id=reservation.time_slot_id,
                status=reservation.status
            )

            # 发送提醒通知
            notification_service.send_reservation_reminder(reservation_read)

    """
    预约的确认可以有以下几种触发条件:

    - 用户在创建预约后的一定时间内(例如24小时)主动确认预约。
    - 管理员或系统在预约开始前的一定时间(例如48小时)自动确认预约。
    - 用户在预约开始时到达场馆,工作人员手动确认预约。
    """
    def confirm_reservation(self, reservation_id: int) -> None:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")

        if reservation.status != ReservationStatus.PENDING:
            raise ValueError("Reservation is not in pending status")

        # 检查确认预约的截止时间(例如,预约创建后的24小时内)
        if reservation.created_at < datetime.now() - timedelta(hours=24):
            raise ValueError("Reservation confirmation deadline has passed")

        reservation.status = ReservationStatus.CONFIRMED
        self.db.commit()

        # 通知用户预约已确认
        self.notification_service.notify_user(reservation.user_id, "Your reservation has been confirmed.")

    def auto_confirm_reservations(self) -> None:
        # 查询所有未确认且开始时间在未来48小时内的预约
        pending_reservations = self.db.query(Reservation).join(ReservationTimeSlot).filter(
            Reservation.status == ReservationStatus.PENDING,
            ReservationTimeSlot.start_time < datetime.now() + timedelta(hours=48),
            ReservationTimeSlot.start_time > datetime.now()
        ).all()

        for reservation in pending_reservations:
            reservation.status = ReservationStatus.CONFIRMED
            self.db.commit()

            # 通知用户预约已自动确认
            self.notification_service.notify_user(reservation.user_id,
                                                  "Your reservation has been automatically confirmed.")

    # 场馆临时关闭或预约时段调整
    def handle_venue_closure_or_time_slot_adjustment(self, venue_id: int, start_date: datetime,
                                                     end_date: datetime) -> None:
        # 查询在指定时间范围内且场馆为指定场馆的预约时段
        affected_time_slots = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id,
            ReservationTimeSlot.date >= start_date.date(),
            ReservationTimeSlot.date <= end_date.date()
        ).all()

        # 获取受影响的预约
        affected_reservations: List[Reservation] = []
        for time_slot in affected_time_slots:
            reservations = self.db.query(Reservation).filter(
                Reservation.time_slot_id == time_slot.id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
            ).all()
            affected_reservations.extend(reservations)

        # 实例化通知服务
        notification_service = NotificationService()

        # 处理受影响的预约
        for reservation in affected_reservations:
            reservation_read = ReservationRead(
                id=reservation.id,
                user_id=reservation.user_id,
                time_slot_id=reservation.time_slot_id,
                status=reservation.status
            )

            # 取消预约
            reservation.status = ReservationStatus.CANCELLED
            self.db.commit()

            # 发送预约取消通知
            notification_service.send_reservation_cancellation_notice(reservation_read)

        # 删除受影响的预约时段
        for time_slot in affected_time_slots:
            self.db.delete(time_slot)
        self.db.commit()
