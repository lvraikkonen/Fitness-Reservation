import logging
from typing import List, Union, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, select
from datetime import datetime, timedelta, date
from app.core.config import settings

from app.models.sport_venue import SportVenue
from app.models.user import User
from app.models.venue import Venue
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.waiting_list import WaitingList
from app.schemas.reservation import (ReservationCreate, ReservationUpdate, ReservationTimeSlotRead,
                                     ReservationRead, PaginatedReservationResponse)
from app.schemas.reservation import VenueCalendarResponse, CalendarTimeSlot
from app.schemas.reservation_time_slot import ReservationTimeSlotBase
from app.schemas.waiting_list import WaitingListReadWithReservationTimeSlot, WaitingListRead

from app.services.notification_service import NotificationService
# from app.services.log_services import log_operation

from app.core.exceptions import ReservationException, ReservationNotFoundError, DatabaseError

logger = logging.getLogger(__name__)


# 常量定义
CANCELLATION_DEADLINE_HOURS = settings.CANCELLATION_DEADLINE_HOURS  # 允许取消的截止时间（小时）


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db=self.db)

    def get_reservations(self, user_id: int):
        return self.db.query(Reservation).filter(Reservation.user_id == user_id).all()

    def get_reservation(self, reservation_id: int) -> Optional[ReservationRead]:
        reservation = (
            self.db.query(Reservation)
            .options(
                joinedload(Reservation.time_slot)
                .joinedload(ReservationTimeSlot.venue)
                .joinedload(Venue.sport_venue)
            )
            .filter(Reservation.id == reservation_id)
            .first()
        )

        if not reservation:
            return None

        return ReservationRead(
            id=reservation.id,
            user_id=reservation.user_id,
            time_slot_id=reservation.time_slot_id,
            status=reservation.status,
            date=reservation.time_slot.date,
            start_time=reservation.time_slot.start_time,
            end_time=reservation.time_slot.end_time,
            sport_venue_name=reservation.time_slot.venue.sport_venue.name,
            venue_name=reservation.time_slot.venue.name
        )

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

    def get_reservations_by_venue(self, venue_id: int):
        # 首先获取该venue的所有time slots
        time_slots = self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.venue_id == venue_id).all()

        # 获取这些time slots对应的所有reservations
        time_slot_ids = [slot.id for slot in time_slots]
        reservations = self.db.query(Reservation).filter(Reservation.time_slot_id.in_(time_slot_ids)).all()

        return reservations

    def get_user_reservations(
            self,
            user_id: int,
            venue_id: Optional[int] = None,
            status: Optional[ReservationStatus] = None,
            page: int = 1,
            page_size: int = 20
    ) -> PaginatedReservationResponse:
        """
        Retrieve paginated reservations for a specific user.

        This method fetches reservations for a given user, with optional filtering by venue and status.
        The results are paginated for efficient data handling.
        """
        try:
            # 构建基础查询
            query = (
                select(Reservation)
                .join(ReservationTimeSlot, Reservation.time_slot_id == ReservationTimeSlot.id)
                .join(Venue, ReservationTimeSlot.venue_id == Venue.id)
                .join(SportVenue, Venue.sport_venue_id == SportVenue.id)
                .options(
                    joinedload(Reservation.time_slot)
                    .joinedload(ReservationTimeSlot.venue)
                    .joinedload(Venue.sport_venue)
                )
                .where(Reservation.user_id == user_id)
            )

            if venue_id:
                query = query.where(Venue.id == venue_id)

            if status:
                query = query.where(Reservation.status == status)

            # 执行查询
            result = self.db.execute(query)
            reservations = result.unique().scalars().all()

            # 计算总数
            total_count = self.db.query(Reservation).filter(Reservation.user_id == user_id).count()

            # 应用分页
            paginated_reservations = reservations[(page - 1) * page_size: page * page_size]

            if not paginated_reservations:
                raise ReservationNotFoundError(f"No reservations found for user {user_id}")

            reservation_reads = [
                ReservationRead(
                    id=r.id,
                    user_id=r.user_id,
                    time_slot_id=r.time_slot_id,
                    status=r.status,
                    date=r.time_slot.date,
                    start_time=r.time_slot.start_time,
                    end_time=r.time_slot.end_time,
                    sport_venue_name=r.time_slot.venue.sport_venue.name,
                    venue_name=r.time_slot.venue.name
                ) for r in paginated_reservations
            ]

            return PaginatedReservationResponse(
                reservations=reservation_reads,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
        except ReservationException as e:
            logging.error(f"Reservation error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in get_user_reservations: {str(e)}")
            raise ReservationException("An unexpected error occurred")

    def get_venue_calendar(
            self,
            venue_id: int,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            page: int = 1,
            page_size: int = 10
    ) -> VenueCalendarResponse:
        # 参数验证
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date cannot be later than end_date")

        # 查询场馆
        venue = self.db.query(Venue).join(SportVenue).filter(Venue.id == venue_id).first()
        if not venue:
            raise ValueError(f"Venue with id {venue_id} not found")

        # 构建查询对象
        query = (
            self.db.query(ReservationTimeSlot)
            .options(joinedload(ReservationTimeSlot.reservations))
            .filter(ReservationTimeSlot.venue_id == venue_id)
            .order_by(ReservationTimeSlot.date, ReservationTimeSlot.start_time)
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
        calendar_data: Dict[date, List[CalendarTimeSlot]] = {}
        for time_slot in reservation_time_slots:
            time_slot_data = CalendarTimeSlot(
                id=time_slot.id,
                date=time_slot.date,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time,
                reservations=[
                    ReservationRead(
                        id=res.id,
                        user_id=res.user_id,
                        time_slot_id=res.time_slot_id,
                        status=res.status,
                        date=time_slot.date,
                        start_time=time_slot.start_time,
                        end_time=time_slot.end_time,
                        sport_venue_name=venue.sport_venue.name,
                        venue_name=venue.name
                    )
                    for res in time_slot.reservations
                ]
            )

            if time_slot.date not in calendar_data:
                calendar_data[time_slot.date] = []
            calendar_data[time_slot.date].append(time_slot_data)

        return VenueCalendarResponse(
            venue_id=venue_id,
            venue_name=venue.name,
            sport_venue_name=venue.sport_venue.name,
            calendar_data=calendar_data,
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            page_size=page_size
        )

    def check_reservation_conflict(self, venue_id: int, reservation_data: ReservationTimeSlotBase) -> Tuple[bool, Optional[str]]:
        # 参数验证
        if reservation_data.start_time >= reservation_data.end_time:
            return True, "Invalid time range: start time must be before end time"

        # 获取场馆信息
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            return True, f"Venue with id {venue_id} not found"

        # 检查与现有预约的冲突
        conflicting_reservations = self._get_conflicting_reservations(venue_id, reservation_data)
        conflicting_count = conflicting_reservations.count()

        # 检查可用名额
        if conflicting_count >= venue.capacity:
            return True, "No available slots for this time period"

        # 检查领导预留时间冲突
        leader_conflict = self._get_conflicting_leader_reserved_time(venue_id, reservation_data)
        if leader_conflict:
            return True, "Conflict with leader reserved time"

        return False, None

    def _get_conflicting_reservations(self, venue_id: int, reservation_data: ReservationTimeSlotBase):
        """检查与现有预约的冲突"""
        return self.db.query(Reservation).join(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == venue_id,
            ReservationTimeSlot.date == reservation_data.date,
            ReservationTimeSlot.start_time < reservation_data.end_time,
            ReservationTimeSlot.end_time > reservation_data.start_time,
            Reservation.status != ReservationStatus.CANCELLED
        )

    def _get_conflicting_leader_reserved_time(self, venue_id: int, reservation_data: ReservationTimeSlotBase):
        """检查领导预留时间冲突"""
        return self.db.query(LeaderReservedTime).filter(
            LeaderReservedTime.venue_id == venue_id,
            LeaderReservedTime.day_of_week == reservation_data.date.weekday(),
            LeaderReservedTime.start_time < reservation_data.end_time,
            LeaderReservedTime.end_time > reservation_data.start_time
        ).first()

    # 创建预约
    def create_reservation(self, reservation_data: ReservationCreate) -> Union[ReservationRead, WaitingListRead]:
        try:
            result = self._create_reservation_logic(reservation_data)
            # 显式提交事务
            self.db.commit()

            # 验证数据是否被正确保存
            if isinstance(result, ReservationRead):
                verification = self.db.query(Reservation).filter(Reservation.id == result.id).first()
                if not verification:
                    raise DatabaseError("Reservation was not found in the database after creation")

            # 发送通知（如果需要）
            if isinstance(result, ReservationRead):
                self._notify_reservation_created(result)
            elif isinstance(result, WaitingListRead):
                self._notify_added_to_waiting_list(result)

            return result
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while creating reservation: {str(e)}")
            raise DatabaseError(f"Database error occurred while creating reservation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during reservation creation: {str(e)}")
            raise

    def _create_reservation_logic(self, reservation_data: ReservationCreate) -> Union[ReservationRead, WaitingListRead]:
        try:
            # 创建 ReservationTimeSlotBase 对象
            time_slot_data = ReservationTimeSlotBase(
                date=reservation_data.date,
                start_time=reservation_data.start_time,
                end_time=reservation_data.end_time
            )

            # 检查预约冲突
            conflict, conflict_reason = self.check_reservation_conflict(reservation_data.venue_id, time_slot_data)

            if conflict:
                logger.info(f"Reservation conflict detected: {conflict_reason}. Adding to waiting list.")
                waiting_list_item = self.join_waiting_list(
                    venue_id=reservation_data.venue_id,
                    reservation_data=time_slot_data,
                    user_id=reservation_data.user_id
                )
                return WaitingListRead.from_orm(waiting_list_item)
            else:
                # 获取或创建时间段
                reservation_time_slot = self._get_or_create_time_slot(reservation_data)

                # 创建新预约
                new_reservation = Reservation(
                    user_id=reservation_data.user_id,
                    time_slot_id=reservation_time_slot.id,
                    status=ReservationStatus.PENDING
                )
                self.db.add(new_reservation)
                self.db.flush()

                logger.info(f"New reservation created with ID: {new_reservation.id}")

                # 验证预约是否被正确保存
                reservation_with_details = self._get_reservation_details(new_reservation.id)
                if not reservation_with_details:
                    raise ValueError(f"Failed to retrieve created reservation with ID: {new_reservation.id}")

                # 创建并返回 ReservationRead 对象
                return ReservationRead(
                    id=reservation_with_details.id,
                    user_id=reservation_with_details.user_id,
                    time_slot_id=reservation_with_details.time_slot_id,
                    status=reservation_with_details.status,
                    date=reservation_with_details.time_slot.date,
                    start_time=reservation_with_details.time_slot.start_time,
                    end_time=reservation_with_details.time_slot.end_time,
                    sport_venue_name=reservation_with_details.time_slot.venue.sport_venue.name,
                    venue_name=reservation_with_details.time_slot.venue.name
                )

        except SQLAlchemyError as e:
            logger.error(f"Database error occurred while creating reservation: {str(e)}")
            raise DatabaseError(f"Failed to create reservation: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating reservation: {str(e)}")
            raise

    def _notify_reservation_created(self, reservation: ReservationRead):
        # 实现发送预约创建通知的逻辑
        pass

    def _notify_added_to_waiting_list(self, waiting_list_item: WaitingListRead):
        # 实现发送加入等待列表通知的逻辑
        pass

    def _get_or_create_time_slot(self, reservation_data: ReservationCreate) -> ReservationTimeSlot:
        reservation_time_slot = self.db.query(ReservationTimeSlot).filter(
            ReservationTimeSlot.venue_id == reservation_data.venue_id,
            ReservationTimeSlot.date == reservation_data.date,
            ReservationTimeSlot.start_time == reservation_data.start_time,
            ReservationTimeSlot.end_time == reservation_data.end_time
        ).first()

        if not reservation_time_slot:
            reservation_time_slot = ReservationTimeSlot(
                venue_id=reservation_data.venue_id,
                date=reservation_data.date,
                start_time=reservation_data.start_time,
                end_time=reservation_data.end_time
            )
            self.db.add(reservation_time_slot)
            self.db.flush()

        return reservation_time_slot

    def _get_reservation_details(self, reservation_id: int) -> Reservation:
        return (
            self.db.query(Reservation)
            .options(
                joinedload(Reservation.time_slot)
                .joinedload(ReservationTimeSlot.venue)
                .joinedload(Venue.sport_venue)
            )
            .filter(Reservation.id == reservation_id)
            .first()
        )

    # 取消预约
    def cancel_reservation(self, reservation_id: int, user_id: int) -> None:
        try:
            reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).with_for_update().first()
            if not reservation:
                raise ValueError(f"Reservation with id {reservation_id} not found")

            # 检查用户权限
            if not self._can_cancel_reservation(reservation, user_id):
                raise ValueError(f"User {user_id} is not authorized to cancel reservation {reservation_id}")

            # 检查预约状态
            if reservation.status == ReservationStatus.CANCELLED:
                raise ValueError(f"Reservation {reservation_id} is already cancelled")

            # 检查取消时间
            if not self._is_cancellation_allowed(reservation):
                raise ValueError(f"Cannot cancel reservation {reservation_id} as it's too close to the start time")

            # 更新预约状态为已取消
            reservation.status = ReservationStatus.CANCELLED
            reservation.cancelled_at = datetime.now()  # 记录取消时间
            logger.info(f"Reservation {reservation_id} has been cancelled by user {user_id}")

            self._handle_waiting_list(reservation)

            # 显式提交事务
            self.db.commit()

            # 通知原预约用户预约已取消
            self._notify_cancellation(reservation)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while cancelling reservation {reservation_id}: {str(e)}")
            raise DatabaseError(f"Failed to cancel reservation: {str(e)}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occurred while cancelling reservation {reservation_id}: {str(e)}")
            raise

    def _can_cancel_reservation(self, reservation: Reservation, user_id: int) -> bool:
        # 检查用户是否是预约的创建者或管理员
        is_creator = reservation.user_id == user_id
        is_admin = self.db.query(User).filter(User.id == user_id, User.role == User.admin_role()).first() is not None
        return is_creator or is_admin

    def _is_cancellation_allowed(self, reservation: Reservation) -> bool:
        # 检查是否在允许取消的时间范围内
        cancellation_deadline = reservation.time_slot.start_time - timedelta(hours=CANCELLATION_DEADLINE_HOURS)
        return datetime.now() <= cancellation_deadline

    def _handle_waiting_list(self, cancelled_reservation: Reservation) -> None:
        waiting_list = self.db.query(WaitingList).filter(
            WaitingList.reservation_id == cancelled_reservation.time_slot_id
        ).order_by(WaitingList.created_at).all()

        if waiting_list:
            # 如果等待列表不为空,将第一个等待的用户分配到预约
            waiting_user = waiting_list[0]
            new_reservation = Reservation(
                user_id=waiting_user.user_id,
                time_slot_id=cancelled_reservation.time_slot_id,
                status=ReservationStatus.PENDING
            )
            self.db.add(new_reservation)
            self.db.delete(waiting_user)
            logger.info(f"User {waiting_user.user_id} moved from waiting list to reservation for time slot {cancelled_reservation.time_slot_id}")

            self._notify_reservation_available(waiting_user.user_id, new_reservation.id)

    def _notify_cancellation(self, reservation: Reservation) -> None:
        self.notification_service.notify_user(
            user_id=reservation.user_id,
            title="Reservation Canceled",
            content=f"Your reservation {reservation.id} has been canceled.",
            type="RES_CANCEL"
        )
        logger.info(f"Cancellation notification sent to user {reservation.user_id} for reservation {reservation.id}")

    def _notify_reservation_available(self, user_id: int, reservation_id: int) -> None:
        self.notification_service.notify_user(
            user_id=user_id,
            title="Reservation Available",
            content=f"Your reservation {reservation_id} is now available!",
            type="RES_AVAIL"
        )
        logger.info(f"Reservation available notification sent to user {user_id} for reservation {reservation_id}")

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
        try:
            # 检查是否已在事务中
            if self.db.in_transaction():
                logger.info("Using existing transaction for reservation confirmation.")
                self._confirm_reservation_logic(reservation_id)
            else:
                logger.info("Starting new transaction for reservation confirmation.")
                with self.db.begin():
                    self._confirm_reservation_logic(reservation_id)

            logger.info(f"Reservation {reservation_id} has been confirmed.")
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred while confirming reservation {reservation_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error occurred while confirming reservation {reservation_id}: {str(e)}")
            raise

    def _confirm_reservation_logic(self, reservation_id: int) -> None:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).with_for_update().first()
        if not reservation:
            raise ValueError(f"Reservation with id {reservation_id} not found")

        if reservation.status != ReservationStatus.PENDING:
            raise ValueError(f"Reservation {reservation_id} is not in pending status")

        if reservation.created_at < datetime.now() - timedelta(hours=24):
            raise ValueError(f"Confirmation deadline has passed for reservation {reservation_id}")

        reservation.status = ReservationStatus.CONFIRMED

        # 通知用户预约已确认
        self.notification_service.notify_user(
            user_id=reservation.user_id,
            title="Reservation Confirmed",
            content=f"Your reservation {reservation_id} has been confirmed.",
            type="RESERVATION_CONFIRMATION"
        )

    def auto_confirm_reservations(self) -> None:
        try:
            if self.db.in_transaction():
                logger.info("Using existing transaction for auto-confirmation.")
                self._auto_confirm_reservations_logic()
            else:
                logger.info("Starting new transaction for auto-confirmation.")
                with self.db.begin():
                    self._auto_confirm_reservations_logic()

            logger.info("Auto-confirmation process completed.")
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred during auto-confirmation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error occurred during auto-confirmation: {str(e)}")
            raise

    def _auto_confirm_reservations_logic(self) -> None:
        # 查询所有未确认且开始时间在未来48小时内的预约
        pending_reservations = self.db.query(Reservation).join(ReservationTimeSlot).filter(
            Reservation.status == ReservationStatus.PENDING,
            ReservationTimeSlot.start_time < datetime.now() + timedelta(hours=48),
            ReservationTimeSlot.start_time > datetime.now()
        ).with_for_update().all()

        for reservation in pending_reservations:
            reservation.status = ReservationStatus.CONFIRMED
            self.notification_service.notify_user(
                user_id=reservation.user_id,
                title="Reservation Auto-Confirmed",
                content=f"Your reservation {reservation.id} has been automatically confirmed.",
                type="AUTO_CONFIRMATION"
            )

        logger.info(f"Auto-confirmed {len(pending_reservations)} reservations.")

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
