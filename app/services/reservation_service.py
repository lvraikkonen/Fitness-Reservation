import logging
from typing import List, Union, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, select
from datetime import datetime, timedelta, date
from app.core.config import settings

from app.models.sport_venue import SportVenue
from app.models.user import User, UserRole
from app.models.venue import Venue
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_rules import ReservationRules
from app.models.recurring_reservation import RecurringReservation, RecurrencePattern
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.waiting_list import WaitingList
from app.schemas.reservation import (ReservationCreate, ReservationUpdate, VenueAvailableTimeSlotRead,
                                     ReservationRead, ReservationDetailRead, PaginatedReservationResponse,
                                     ConflictCheckResult, RecurringReservationRead, RecurringReservationUpdate,
                                     RecurringReservationCreate)
from app.schemas.reservation import VenueCalendarResponse, CalendarTimeSlot, ReservationConfirmationResult
from app.schemas.waiting_list import WaitingListReadWithVenueAvailableTimeSlot, WaitingListRead
from app.schemas.venue_available_time_slot import VenueAvailableTimeSlotRead, VenueAvailabilityRead
from app.services.notification_service import NotificationService
from app.services.waiting_list_service import WaitingListService
from app.services.venue_available_time_slot_service import VenueAvailableTimeSlotService

from app.core.exceptions import (ReservationException, ReservationNotFoundError, DatabaseError,
                                 InvalidCheckInTimeError, InvalidReservationStatusError)
from app.core.config import get_logger
from contextlib import contextmanager
# add check-in func
import jwt

logger = get_logger(__name__)


# 常量定义
CANCELLATION_DEADLINE_HOURS = settings.CANCELLATION_DEADLINE_HOURS  # 允许取消的截止时间（小时）
WAITING_LIST_PROCESS_HOURS = settings.WAITING_LIST_PROCESS_HOURS  # WaitingList过期时间
RESERVATION_CONFIRMATION_DEADLINE_HOURS = settings.RESERVATION_CONFIRMATION_DEADLINE_HOURS  # 预约确认截止时间
AUTO_CONFIRM_HOURS = settings.AUTO_CONFIRM_HOURS  # 预约自动确认时间


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db=self.db)
        self.venue_available_time_slot_service = VenueAvailableTimeSlotService(db=self.db)
        self.waiting_list_service = WaitingListService(db=self.db)

    # add context manager
    @contextmanager
    def transaction(self):
        try:
            yield
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise

    def get_reservation(self, reservation_id: int) -> Optional[ReservationRead]:
        reservation = (
            self.db.query(Reservation)
            .options(
                joinedload(Reservation.venue_available_time_slot)
                .joinedload(VenueAvailableTimeSlot.venue)
                .joinedload(Venue.sport_venue)
            )
            .filter(Reservation.id == reservation_id)
            .first()
        )

        if not reservation:
            return None

        return ReservationService.create_reservation_read(reservation)

    def get_all_reservations(self, skip: int = 0, limit: int = 100) -> Tuple[List[ReservationRead], int]:
        query = (
            self.db.query(Reservation)
            .options(
                joinedload(Reservation.venue_available_time_slot),
                joinedload(Reservation.venue).joinedload(Venue.sport_venue)
            )
            .order_by(Reservation.created_at.desc())
        )

        total_count = query.count()
        reservations = query.offset(skip).limit(limit).all()

        reservation_reads = [ReservationService.create_reservation_read(res) for res in reservations]

        return reservation_reads, total_count

    def update_reservation(self, reservation_id: int, reservation: ReservationUpdate):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            update_data = reservation.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reservation, key, value)

            # 如果更新了时间段,需要相应更新 VenueAvailableTimeSlot
            if 'venue_available_time_slot_id' in update_data:
                old_slot = self.db.query(VenueAvailableTimeSlot).get(db_reservation.venue_available_time_slot_id)
                new_slot = self.db.query(VenueAvailableTimeSlot).get(update_data['venue_available_time_slot_id'])

                if old_slot and new_slot:
                    old_slot.capacity += 1
                    new_slot.capacity -= 1

            self.db.commit()
            self.db.refresh(db_reservation)
        return db_reservation

    def get_user_reservations(
            self,
            user_id: int,
            venue_id: Optional[int] = None,
            status: Optional[ReservationStatus] = None,
            page: int = 1,
            page_size: int = 20
    ) -> PaginatedReservationResponse:
        try:
            # 构建基础查询
            query = (
                select(Reservation)
                .join(VenueAvailableTimeSlot, Reservation.venue_available_time_slot_id == VenueAvailableTimeSlot.id)
                .join(Venue, VenueAvailableTimeSlot.venue_id == Venue.id)
                .join(SportVenue, Venue.sport_venue_id == SportVenue.id)
                .options(
                    joinedload(Reservation.venue_available_time_slot)
                    .joinedload(VenueAvailableTimeSlot.venue)
                    .joinedload(Venue.sport_venue),
                    joinedload(Reservation.user)
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

            reservation_detail_reads = [
                ReservationService.create_reservation_detail_read(r) for r in paginated_reservations
            ]

            return PaginatedReservationResponse(
                reservations=reservation_detail_reads,
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
            self.db.query(VenueAvailableTimeSlot)
            .options(joinedload(VenueAvailableTimeSlot.reservations))
            .filter(VenueAvailableTimeSlot.venue_id == venue_id)
            .order_by(VenueAvailableTimeSlot.date, VenueAvailableTimeSlot.start_time)
        )

        # 添加日期范围过滤
        if start_date:
            query = query.filter(VenueAvailableTimeSlot.date >= start_date)
        if end_date:
            query = query.filter(VenueAvailableTimeSlot.date <= end_date)

        # 添加分页功能
        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        available_time_slots = query.offset(offset).limit(page_size).all()

        # 将预约时段按照日期分组
        calendar_data: Dict[date, List[CalendarTimeSlot]] = {}
        for time_slot in available_time_slots:
            time_slot_data = CalendarTimeSlot(
                id=time_slot.id,
                date=time_slot.date,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time,
                capacity=time_slot.capacity,
                reservations=[
                    ReservationService.create_reservation_read(res)
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

    def check_reservation_conflict(self, reservation_data: ReservationCreate) -> ConflictCheckResult:
        try:
            # 获取场馆信息
            venue = self.db.query(Venue).filter(Venue.id == reservation_data.venue_id).first()
            if not venue:
                return ConflictCheckResult(
                    has_conflict=True,
                    conflict_reason=f"Venue with id {reservation_data.venue_id} not found"
                )

            # 检查与现有预约的冲突
            conflicting_slots = self._get_conflicting_time_slots(reservation_data)

            if conflicting_slots:
                return ConflictCheckResult(
                    has_conflict=True,
                    conflict_reason="Conflict with existing reservations",
                    conflicting_slots=[{
                        "date": slot.date,
                        "start_time": slot.start_time,
                        "end_time": slot.end_time
                    } for slot in conflicting_slots]
                )

            # 检查领导预留时间冲突
            leader_conflict = self._get_conflicting_leader_reserved_time(reservation_data)
            if leader_conflict:
                return ConflictCheckResult(
                    has_conflict=True,
                    conflict_reason="Conflict with leader reserved time",
                    conflicting_slots=[{
                        "day_of_week": leader_conflict.day_of_week,
                        "start_time": leader_conflict.start_time,
                        "end_time": leader_conflict.end_time
                    }]
                )

            # 如果是周期性预约，检查未来的冲突
            if reservation_data.is_recurring:
                future_conflicts = self._check_recurring_conflicts(reservation_data)
                if future_conflicts:
                    return ConflictCheckResult(
                        has_conflict=True,
                        conflict_reason="Conflict with future reservations",
                        conflicting_slots=future_conflicts
                    )

            return ConflictCheckResult(has_conflict=False)

        except Exception as e:
            logger.error(f"Error checking reservation conflict: {str(e)}")
            return ConflictCheckResult(
                has_conflict=True,
                conflict_reason=f"An error occurred while checking conflicts: {str(e)}"
            )

    def _get_conflicting_time_slots(self, reservation_data: ReservationCreate) -> List[VenueAvailableTimeSlot]:
        return self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == reservation_data.venue_id,
            VenueAvailableTimeSlot.date == reservation_data.date,
            VenueAvailableTimeSlot.start_time < reservation_data.end_time,
            VenueAvailableTimeSlot.end_time > reservation_data.start_time,
            VenueAvailableTimeSlot.capacity <= 0
        ).all()

    def _get_conflicting_leader_reserved_time(
            self, reservation_data: ReservationCreate) -> Optional[LeaderReservedTime]:
        return self.db.query(LeaderReservedTime).filter(
            LeaderReservedTime.venue_id == reservation_data.venue_id,
            LeaderReservedTime.day_of_week == reservation_data.date.weekday(),
            LeaderReservedTime.start_time < reservation_data.end_time,
            LeaderReservedTime.end_time > reservation_data.start_time
        ).first()

    def _check_recurring_conflicts(self, reservation_data: ReservationCreate) -> List[Dict[str, Any]]:
        # 实现检查周期性预约冲突的逻辑
        # 这里需要根据 recurring_pattern 和 recurrence_end_date 生成未来的预约日期
        # 然后检查这些日期是否有冲突
        # 返回冲突的日期和时间列表
        pass

    # 创建预约
    def create_reservation(
            self, reservation_data: ReservationCreate
    ) -> Union[List[ReservationRead], List[WaitingListRead]]:
        logger.info(f"Attempting to create reservation: {reservation_data}")
        try:
            with self.transaction():
                results = self._create_reservation_logic(reservation_data)
                logger.debug(f"Reservation creation logic completed. Results: {results}")

                # 验证数据是否被正确保存
                if isinstance(results[0], ReservationRead):
                    for result in results:
                        verification = self.db.query(Reservation).filter(Reservation.id == result.id).first()
                        if not verification:
                            raise DatabaseError(
                                f"Reservation with id {result.id} was not found in the database after creation")
                        logger.debug(f"Reservation verified in database: {verification}")

            # 发送通知
            if results:
                if isinstance(results[0], ReservationRead):
                    for result in results:
                        ReservationService._notify_reservation_created(result)
                        logger.info(f"Notification sent for created reservation: {result.id}")
                elif isinstance(results[0], WaitingListRead):
                    for result in results:
                        ReservationService._notify_added_to_waiting_list(result)
                        logger.info(f"Notification sent for waiting list addition: {result.id}")
                else:
                    logger.warning(f"Unexpected result type: {type(results[0])}")
            else:
                logger.warning("No results returned from _create_reservation_logic")

            return results
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred while creating reservation: {str(e)}")
            raise DatabaseError(f"Database error occurred while creating reservation: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during reservation creation: {str(e)}")
            raise

    def _create_reservation_logic(
            self,
            reservation_data: ReservationCreate
    ) -> Union[List[ReservationRead], List[WaitingListRead]]:
        try:
            # 1. 验证用户
            user = self.db.query(User).filter(User.id == reservation_data.user_id).first()
            if not user:
                raise ReservationException("User not found")

            # 2. 获取场馆和预约规则
            venue = self.db.query(Venue).filter(Venue.id == reservation_data.venue_id).first()
            if not venue:
                raise ReservationException("Venue not found")

            reservation_rules = self.db.query(ReservationRules).filter(
                ReservationRules.venue_id == venue.id,
                ReservationRules.user_role == user.role
            ).first()
            if not reservation_rules:
                raise ReservationException("Reservation rules not found for this user role and venue")

            # 3. 检查用户是否超过预约次数限制
            self._check_reservation_limit(user, venue, reservation_rules)

            # 4. 获取并验证可用时间段
            available_slot = self._get_containing_available_slot(reservation_data, venue.id)
            if available_slot is None:
                # 处理没有找到合适时间段的情况
                raise ReservationException("No available time slot for the requested reservation")

            reservations = []
            waiting_list_items = []

            # 5. 检查容量并创建预约或加入等待列表
            if available_slot.capacity <= 0:
                # 如果没有可用容量，加入等待列表
                waiting_list_item = self.join_waiting_list(
                    venue.id,
                    reservation_data,
                    user.id
                )[0]  # 获取列表中的第一个（也是唯一的）项目
                waiting_list_items.append(waiting_list_item)
            else:
                # 创建预约
                new_reservation = Reservation(
                    user_id=user.id,
                    venue_id=venue.id,
                    venue_available_time_slot_id=available_slot.id,
                    status=ReservationStatus.PENDING,
                    date=reservation_data.date,  # 用户实际预约日期
                    actual_start_time=reservation_data.start_time,
                    actual_end_time=reservation_data.end_time,  # 用户实际预约时间段
                    is_recurring=reservation_data.is_recurring,

                )
                self.db.add(new_reservation)
                reservations.append(new_reservation)

                # 6. 处理周期性预约
                if reservation_data.is_recurring:
                    recurring_reservation = self._create_recurring_reservation(reservation_data, user.id, venue.id)
                    new_reservation.recurring_reservation_id = recurring_reservation.id

                # 更新时间段容量
                available_slot.capacity -= 1

            self.db.commit()

            # 7. 转换为ReservationRead对象并返回相应列表
            if reservations:
                return [ReservationService.create_reservation_read(reservation) for reservation in reservations]
            else:
                return [WaitingListRead.from_orm(item) for item in waiting_list_items]

        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error(f"Database error occurred while creating reservation: {str(e)}")
            raise DatabaseError(f"Database error occurred while creating reservation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logging.error(f"Unexpected error during reservation creation: {str(e)}")
            raise ReservationException(str(e))

    @staticmethod
    def create_reservation_read(reservation: Reservation) -> ReservationRead:
        return ReservationRead(
            id=reservation.id,
            user_id=reservation.user_id,
            venue_id=reservation.venue_available_time_slot.venue_id,
            venue_available_time_slot_id=reservation.venue_available_time_slot_id,
            status=reservation.status,
            date=reservation.venue_available_time_slot.date,
            actual_start_time=reservation.actual_start_time,
            actual_end_time=reservation.actual_end_time,
            is_recurring=reservation.is_recurring,
            venue_name=reservation.venue_available_time_slot.venue.name
        )

    @staticmethod
    def create_reservation_detail_read(reservation: Reservation) -> ReservationDetailRead:
        return ReservationDetailRead(
            id=reservation.id,
            user_id=reservation.user_id,
            venue_id=reservation.venue_available_time_slot.venue_id,
            venue_available_time_slot_id=reservation.venue_available_time_slot_id,
            status=reservation.status,
            date=reservation.venue_available_time_slot.date,
            actual_start_time=reservation.actual_start_time,
            actual_end_time=reservation.actual_end_time,
            is_recurring=reservation.is_recurring,
            venue_name=reservation.venue_available_time_slot.venue.name,
            recurring_reservation_id=reservation.recurring_reservation_id,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
            cancelled_at=reservation.cancelled_at,
            checked_in_at=reservation.checked_in_at,
            sport_venue_name=reservation.venue_available_time_slot.venue.sport_venue.name,
            user_name=reservation.user.username,
            venue_available_time_slot_start=reservation.venue_available_time_slot.start_time,
            venue_available_time_slot_end=reservation.venue_available_time_slot.end_time
        )

    def _check_reservation_limit(self, user: User, venue: Venue, rules: ReservationRules):
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        daily_count = self.db.query(Reservation).filter(
            Reservation.user_id == user.id,
            Reservation.venue_id == venue.id,
            Reservation.created_at >= today
        ).count()

        weekly_count = self.db.query(Reservation).filter(
            Reservation.user_id == user.id,
            Reservation.venue_id == venue.id,
            Reservation.created_at >= week_start
        ).count()

        monthly_count = self.db.query(Reservation).filter(
            Reservation.user_id == user.id,
            Reservation.venue_id == venue.id,
            Reservation.created_at >= month_start
        ).count()

        if daily_count >= rules.max_daily_reservations:
            raise ReservationException("Daily reservation limit exceeded")
        if weekly_count >= rules.max_weekly_reservations:
            raise ReservationException("Weekly reservation limit exceeded")
        if monthly_count >= rules.max_monthly_reservations:
            raise ReservationException("Monthly reservation limit exceeded")

    # 查找包含所请求时间的可用时间段
    def _get_containing_available_slot(
            self,
            reservation_data: ReservationCreate,
            venue_id: int
    ) -> Optional[VenueAvailableTimeSlot]:
        """
        获取包含请求预约时间的可用时间段。

        :param reservation_data: 预约请求数据
        :param venue_id: 场馆ID
        :return: 包含请求时间的可用时间段，如果没有找到则返回None
        """
        try:
            slot = self.db.query(VenueAvailableTimeSlot).filter(
                and_(
                    VenueAvailableTimeSlot.venue_id == venue_id,
                    VenueAvailableTimeSlot.date == reservation_data.date,
                    VenueAvailableTimeSlot.start_time <= reservation_data.start_time,
                    VenueAvailableTimeSlot.end_time >= reservation_data.end_time,
                    VenueAvailableTimeSlot.capacity > 0
                )
            ).first()

            if slot:
                logger.info(f"Found available time slot: id={slot.id}, date={slot.date}, "
                            f"start_time={slot.start_time}, end_time={slot.end_time}, with capacity={slot.capacity}")
            else:
                logger.warning(f"No available time slot found for reservation: venue_id={venue_id}, "
                               f"date={reservation_data.date}, start_time={reservation_data.start_time}, "
                               f"end_time={reservation_data.end_time}")

            return slot

        except Exception as e:
            logger.error(f"Error occurred while getting available time slot: {str(e)}")
            return None

    def _create_recurring_reservation(self, reservation_data: ReservationCreate, user_id: int,
                                      venue_id: int) -> RecurringReservation:
        recurring_reservation = RecurringReservation(
            user_id=user_id,
            venue_id=venue_id,
            pattern=reservation_data.recurrence_pattern,
            start_date=reservation_data.date,
            end_date=reservation_data.recurrence_end_date
        )
        self.db.add(recurring_reservation)
        return recurring_reservation

    @staticmethod
    def _notify_reservation_created(reservation: ReservationRead):
        # 实现发送预约创建通知的逻辑
        logger.info(f"Reservation creation notification sent for reservation ID: {reservation.id}")
        # try:
        #     self.notification_service.send_notification(
        #         user_id=reservation.user_id,
        #         title="Reservation Created",
        #         content=f"Your reservation for {reservation.venue_name} on {reservation.date} from {reservation.start_time} to {reservation.end_time} has been created.",
        #         notification_type="RESERVATION_CREATED"
        #     )
        #     logging.info(f"Reservation creation notification sent for reservation ID: {reservation.id}")
        # except Exception as e:
        #     logging.error(f"Failed to send reservation creation notification: {str(e)}")

    @staticmethod
    def _notify_added_to_waiting_list(waiting_list_item: WaitingListRead):
        # 实现发送加入等待列表通知的逻辑
        logger.info(f"Added to waiting list notification sent for user ID: {waiting_list_item.user_id}")
        # try:
        #     venue_available_time_slot = self.db.query(VenueAvailableTimeSlot).filter(VenueAvailableTimeSlot.id == waiting_list_item.venue_available_time_slot_id).first()
        #     if venue_available_time_slot:
        #         self.notification_service.send_notification(
        #             user_id=waiting_list_item.user_id,
        #             title="Added to Waiting List",
        #             content=f"You have been added to the waiting list for {venue_available_time_slot.venue.name} on {venue_available_time_slot.date} from {venue_available_time_slot.start_time} to {venue_available_time_slot.end_time}.",
        #             notification_type="ADDED_TO_WAITING_LIST"
        #         )
        #         logging.info(f"Added to waiting list notification sent for user ID: {waiting_list_item.user_id}")
        #     else:
        #         logging.error(f"Failed to find VenueAvailableTimeSlot for waiting list item ID: {waiting_list_item.id}")
        # except Exception as e:
        #     logging.error(f"Failed to send added to waiting list notification: {str(e)}")

    # 取消预约
    def cancel_reservation(self, reservation_id: int, user_id: int) -> None:
        try:
            reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).with_for_update().first()
            if not reservation:
                raise ReservationException(f"Reservation with id {reservation_id} not found")

            # 检查用户权限
            if not self._can_cancel_reservation(reservation, user_id):
                raise ReservationException(f"User {user_id} is not authorized to cancel reservation {reservation_id}")

            # 检查预约状态
            if reservation.status == ReservationStatus.CANCELLED:
                raise ReservationException(f"Reservation {reservation_id} is already cancelled")

            # 检查取消时间
            if not self._is_cancellation_allowed(reservation):
                raise ReservationException(
                    f"Cannot cancel reservation {reservation_id} as it's too close to the start time")

            # 更新预约状态为已取消
            reservation.status = ReservationStatus.CANCELLED
            reservation.cancelled_at = datetime.now()  # 记录取消时间
            logger.info(f"Reservation {reservation_id} has been cancelled by user {user_id}")

            # 增加对应时间段的可用容量
            venue_available_time_slot = reservation.venue_available_time_slot
            venue_available_time_slot.capacity += 1

            # 处理等待列表
            self._handle_waiting_list(reservation)

            # 显式提交事务
            self.db.commit()
        except ReservationException as e:
            logger.warning(str(e))
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while cancelling reservation {reservation_id}: {str(e)}")
            raise DatabaseError(f"Failed to cancel reservation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error occurred while cancelling reservation {reservation_id}: {str(e)}")
            raise
        else:
            # 通知原预约用户预约已取消
            self._notify_cancellation(reservation)

    def _can_cancel_reservation(self, reservation: Reservation, user_id: int) -> bool:
        # 检查用户是否是预约的创建者或管理员
        is_creator = reservation.user_id == user_id
        is_admin = self.db.query(User).filter(User.id == user_id, User.role == UserRole.ADMIN).first() is not None
        return is_creator or is_admin

    def _is_cancellation_allowed(self, reservation: Reservation) -> bool:
        # 获取关联的 VenueAvailableTimeSlot
        time_slot = reservation.venue_available_time_slot

        # 组合日期和开始时间
        reservation_datetime = datetime.combine(time_slot.date, time_slot.start_time)

        # 计算取消截止时间
        cancellation_deadline = reservation_datetime - timedelta(hours=CANCELLATION_DEADLINE_HOURS)

        # 检查当前时间是否在允许取消的时间范围内
        return datetime.now() <= cancellation_deadline

    def _handle_waiting_list(self, cancelled_reservation: Reservation) -> None:
        logger.debug(f"Handling waiting list for cancelled reservation: {cancelled_reservation.id}")
        logger.debug(f"Venue available time slot id: {cancelled_reservation.venue_available_time_slot_id}")
        waiting_user = self.waiting_list_service.get_next_waiting_user(
            cancelled_reservation.venue_available_time_slot_id
        )

        if waiting_user:
            new_reservation = Reservation(
                user_id=waiting_user.user_id,
                venue_id=cancelled_reservation.venue_id,
                venue_available_time_slot_id=cancelled_reservation.venue_available_time_slot_id,
                status=ReservationStatus.PENDING
            )
            self.db.add(new_reservation)

            self.waiting_list_service.remove_from_waiting_list(waiting_user)

            logger.info(
                f"User {waiting_user.user_id} moved from waiting list to reservation for time slot {cancelled_reservation.venue_available_time_slot_id}")

            # 减少对应时间段的可用容量
            venue_available_time_slot = cancelled_reservation.venue_available_time_slot
            venue_available_time_slot.capacity -= 1

            self.db.commit()  # 提交事务

            # 发送通知
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
    def join_waiting_list(self, venue_id: int, reservation_data: ReservationCreate, user_id: int) -> List[WaitingList]:
        try:
            # 获取包含用户请求时间的可用时间段
            available_slot = self._get_containing_available_slot(reservation_data, venue_id)

            if not available_slot:
                raise ReservationException("No available time slot found for the requested time")

            waiting_list_items = []

            # 检查用户是否已经在该时间段的等待列表中
            existing_waiting_list_item = self.db.query(WaitingList).filter(
                WaitingList.venue_available_time_slot_id == available_slot.id,
                WaitingList.user_id == user_id
            ).first()

            if existing_waiting_list_item:
                # 如果用户已经在等待列表中，更新实际请求的时间
                existing_waiting_list_item.actual_start_time = reservation_data.start_time
                existing_waiting_list_item.actual_end_time = reservation_data.end_time
                existing_waiting_list_item.date = reservation_data.date
                waiting_list_items.append(existing_waiting_list_item)
            else:
                # 如果用户不在等待列表中，创建新的等待列表项
                new_waiting_list_item = WaitingList(
                    venue_available_time_slot_id=available_slot.id,
                    user_id=user_id,
                    actual_start_time=reservation_data.start_time,  # 用户实际请求时间段
                    actual_end_time=reservation_data.end_time,  # 用户实际请求时间段
                    date=reservation_data.date  # 用户实际请求日期
                )
                self.db.add(new_waiting_list_item)
                waiting_list_items.append(new_waiting_list_item)

            self.db.commit()
            for item in waiting_list_items:
                self.db.refresh(item)

            return waiting_list_items
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to join waiting list: {str(e)}")
            raise ReservationException(f"Failed to join waiting list: {str(e)}")

    # 查看预约等候列表
    def get_waiting_list(self, venue_id: int) -> List[WaitingListReadWithVenueAvailableTimeSlot]:
        # 查询指定场馆的所有等候列表记录,并按照创建时间排序
        waiting_list_records = (
            self.db.query(WaitingList)
            .join(VenueAvailableTimeSlot)
            .filter(VenueAvailableTimeSlot.venue_id == venue_id)
            .options(joinedload(WaitingList.venue_available_time_slot))
            .order_by(WaitingList.created_at)
            .all()
        )

        # 将等候列表记录转换为 WaitingListReadWithVenueAvailableTimeSlot 对象
        waiting_list_read_objects = []
        for waiting_list_record in waiting_list_records:
            venue_available_time_slot = waiting_list_record.venue_available_time_slot
            waiting_list_read_object = WaitingListReadWithVenueAvailableTimeSlot(
                id=waiting_list_record.id,
                user_id=waiting_list_record.user_id,
                venue_available_time_slot_id=waiting_list_record.venue_available_time_slot_id,
                venue_available_time_slot=VenueAvailableTimeSlotRead(
                    id=venue_available_time_slot.id,
                    venue_id=venue_available_time_slot.venue_id,
                    date=venue_available_time_slot.date,
                    start_time=venue_available_time_slot.start_time,
                    end_time=venue_available_time_slot.end_time,
                    capacity=venue_available_time_slot.capacity
                ),
                created_at=waiting_list_record.created_at,
                updated_at=waiting_list_record.updated_at
            )
            waiting_list_read_objects.append(waiting_list_read_object)

        return waiting_list_read_objects

    # 处理等待列表并自动分配预约
    def process_waiting_list(self) -> None:
        current_time = datetime.now()
        process_hours = WAITING_LIST_PROCESS_HOURS
        process_time = current_time + timedelta(hours=process_hours)

        # 查找所有即将在4小时内开始的时间段
        upcoming_time_slots = self.db.query(VenueAvailableTimeSlot).filter(
            and_(
                VenueAvailableTimeSlot.date == current_time.date(),
                VenueAvailableTimeSlot.start_time <= process_time.time(),
                VenueAvailableTimeSlot.start_time > current_time.time()
            )
        ).all()

        for time_slot in upcoming_time_slots:
            # 获取该时间段的等待列表
            waiting_list = self.db.query(WaitingList).filter(
                WaitingList.venue_available_time_slot_id == time_slot.id
            ).order_by(WaitingList.created_at).all()

            # 获取该时间段的可用名额
            reservations_count = self.db.query(Reservation).filter(
                Reservation.venue_available_time_slot_id == time_slot.id,
                Reservation.status != ReservationStatus.CANCELLED
            ).count()
            available_slots = time_slot.capacity - reservations_count

            # 根据可用名额分配预约给等待列表中的用户
            for _ in range(available_slots):
                if waiting_list:
                    waiting_user = waiting_list.pop(0)
                    new_reservation = Reservation(
                        user_id=waiting_user.user_id,
                        venue_id=time_slot.venue_id,
                        venue_available_time_slot_id=time_slot.id,
                        status=ReservationStatus.PENDING
                    )
                    self.db.add(new_reservation)
                    self.db.delete(waiting_user)

                    # 通知新分配的用户他们的预约现在可用
                    self.notification_service.notify_user(
                        waiting_user.user_id,
                        "Your reservation is now available!",
                        "RESERVATION_AVAILABLE"
                    )

            # 将剩余的等待列表条目设置为已过期并通知用户
            for waiting_item in waiting_list:
                waiting_item.is_expired = True
                self.notification_service.notify_user(
                    waiting_item.user_id,
                    "Your waiting list entry has expired.",
                    "WAITING_LIST_EXPIRED"
                )

        self.db.commit()

    def send_reservation_reminder(self) -> None:
        # 获取当前时间
        current_time = datetime.now()
        # 计算提醒时间范围
        reminder_start_time = current_time + timedelta(hours=1)  # 提前1小时提醒
        reminder_end_time = current_time + timedelta(hours=24)  # 提前24小时提醒

        # 查询在提醒时间范围内且状态为 CONFIRMED 的预约
        reservations = self.db.query(Reservation).join(VenueAvailableTimeSlot).filter(
            and_(
                Reservation.status == ReservationStatus.CONFIRMED,
                VenueAvailableTimeSlot.date == current_time.date(),
                VenueAvailableTimeSlot.start_time >= reminder_start_time.time(),
                VenueAvailableTimeSlot.start_time < reminder_end_time.time()
            )
        ).all()

        # 发送预约提醒
        for reservation in reservations:
            reservation_detail = ReservationService.create_reservation_detail_read(reservation)

            # 发送提醒通知
            self.notification_service.send_reservation_reminder(reservation_detail)

    """
    预约的确认可以有以下几种触发条件:

    - 用户在创建预约后的一定时间内(例如24小时)主动确认预约。
    - 管理员或系统在预约开始前的一定时间(例如48小时)自动确认预约。
    - 用户在预约开始时到达场馆,工作人员手动确认预约。
    """
    def confirm_reservation(self, reservation_id: int) -> ReservationConfirmationResult:
        try:
            reservation = self._confirm_reservation_logic(reservation_id)
            self.db.commit()

            confirmation_result = ReservationConfirmationResult(
                reservation_id=reservation.id,
                status=reservation.status,
                confirmed_at=datetime.now(),
                message=f"Reservation {reservation_id} has been successfully confirmed."
            )

            logger.info(f"Reservation {reservation_id} has been confirmed.")
            return confirmation_result
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while confirming reservation {reservation_id}: {str(e)}")
            raise ReservationException(f"Failed to confirm reservation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occurred while confirming reservation {reservation_id}: {str(e)}")
            raise ReservationException(f"Failed to confirm reservation: {str(e)}")

    def _confirm_reservation_logic(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).with_for_update().first()
        if not reservation:
            raise ReservationException(f"Reservation with id {reservation_id} not found")

        if reservation.status != ReservationStatus.PENDING:
            raise ReservationException(f"Reservation {reservation_id} is not in pending status")

        if reservation.created_at < datetime.now() - timedelta(
                hours=RESERVATION_CONFIRMATION_DEADLINE_HOURS):
            raise ReservationException(f"Confirmation deadline has passed for reservation {reservation_id}")

        reservation.status = ReservationStatus.CONFIRMED

        self.notification_service.notify_user(
            user_id=reservation.user_id,
            title="Reservation Confirmed",
            content=f"Your reservation {reservation_id} has been confirmed.",
            type="RESERVATION_CONFIRMATION"
        )
        logger.info(f"Queued confirmation notification for reservation {reservation_id}")

        return reservation

    def auto_confirm_reservations(self) -> List[Reservation]:
        try:
            confirmed_reservations = self._auto_confirm_reservations_logic()
            self.db.commit()
            logger.info(f"Auto-confirmed {len(confirmed_reservations)} reservations.")
            return confirmed_reservations
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred during auto-confirmation: {str(e)}")
            raise ReservationException(f"Failed to auto-confirm reservations: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occurred during auto-confirmation: {str(e)}")
            raise ReservationException(f"Failed to auto-confirm reservations: {str(e)}")

    def _auto_confirm_reservations_logic(self) -> List[Reservation]:
        current_time = datetime.now()
        auto_confirm_time = current_time + timedelta(hours=AUTO_CONFIRM_HOURS)

        pending_reservations = self.db.query(Reservation).join(VenueAvailableTimeSlot).filter(
            and_(
                Reservation.status == ReservationStatus.PENDING,
                VenueAvailableTimeSlot.date == current_time.date(),
                VenueAvailableTimeSlot.start_time <= auto_confirm_time.time(),
                VenueAvailableTimeSlot.start_time > current_time.time()
            )
        ).with_for_update().all()

        confirmed_reservations: List[Reservation] = []

        for reservation in pending_reservations:
            reservation.status = ReservationStatus.CONFIRMED
            confirmed_reservations.append(reservation)

            self.notification_service.notify_user(
                user_id=reservation.user_id,
                title="Reservation Auto-Confirmed",
                content=f"Your reservation {reservation.id} has been automatically confirmed.",
                type="AUTO_CONFIRMATION"
            )

        return confirmed_reservations

    def handle_venue_closure_or_time_slot_adjustment(self, venue_id: int, start_date: datetime,
                                                     end_date: datetime) -> None:
        try:
            # 查询在指定时间范围内且场馆为指定场馆的可用时间段
            affected_time_slots = self.db.query(VenueAvailableTimeSlot).filter(
                VenueAvailableTimeSlot.venue_id == venue_id,
                VenueAvailableTimeSlot.date >= start_date.date(),
                VenueAvailableTimeSlot.date <= end_date.date()
            ).all()

            # 获取受影响的预约
            affected_reservations: List[Reservation] = []
            for time_slot in affected_time_slots:
                reservations = self.db.query(Reservation).filter(
                    Reservation.venue_available_time_slot_id == time_slot.id,
                    Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
                ).all()
                affected_reservations.extend(reservations)

            # 处理受影响的预约
            for reservation in affected_reservations:
                reservation_read = ReservationRead(
                    id=reservation.id,
                    user_id=reservation.user_id,
                    venue_available_time_slot_id=reservation.venue_available_time_slot_id,
                    status=reservation.status,
                    date=reservation.venue_available_time_slot.date,
                    start_time=reservation.venue_available_time_slot.start_time,
                    end_time=reservation.venue_available_time_slot.end_time,
                    venue_name=reservation.venue_available_time_slot.venue.name,
                    sport_venue_name=reservation.venue_available_time_slot.venue.sport_venue.name
                )

                # 取消预约
                reservation.status = ReservationStatus.CANCELLED

                # 发送预约取消通知
                self.notification_service.send_reservation_cancellation_notice(reservation_read)

            # 删除受影响的可用时间段
            for time_slot in affected_time_slots:
                self.db.delete(time_slot)

            self.db.commit()
            logger.info(f"Successfully handled venue closure or time slot adjustment for venue {venue_id}")

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while handling venue closure or time slot adjustment: {str(e)}")
            raise ReservationException(f"Failed to handle venue closure or time slot adjustment: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occurred while handling venue closure or time slot adjustment: {str(e)}")
            raise ReservationException(f"Failed to handle venue closure or time slot adjustment: {str(e)}")

    def create_recurring_reservation(self, recurring_reservation: RecurringReservationCreate,
                                     user_id: int) -> RecurringReservationRead:
        # 实现创建周期性预约的逻辑
        pass

    def get_recurring_reservation(self, recurring_id: int, user_id: int) -> RecurringReservationRead:
        # 实现获取周期性预约的逻辑
        pass

    def update_recurring_reservation(self, recurring_id: int, recurring_reservation: RecurringReservationUpdate,
                                     user_id: int) -> RecurringReservationRead:
        # 实现更新周期性预约的逻辑
        pass

    def delete_recurring_reservation(self, recurring_id: int, user_id: int) -> None:
        # 实现删除周期性预约的逻辑
        pass

    def get_user_reservation_history(self, user_id: int, start_date: Optional[date], end_date: Optional[date],
                                     page: int, page_size: int) -> PaginatedReservationResponse:
        # 实现获取用户预约历史的逻辑
        query = (
            self.db.query(Reservation)
            .join(VenueAvailableTimeSlot)
            .join(Venue)
            .filter(Reservation.user_id == user_id)
            .order_by(VenueAvailableTimeSlot.date.desc(), VenueAvailableTimeSlot.start_time.desc())
        )

        if start_date:
            query = query.filter(VenueAvailableTimeSlot.date >= start_date)
        if end_date:
            query = query.filter(VenueAvailableTimeSlot.date <= end_date)

        total_count = query.count()
        reservations = query.offset((page - 1) * page_size).limit(page_size).all()

        reservation_reads = [
            ReservationService.create_reservation_detail_read(res) for res in reservations
        ]

        return PaginatedReservationResponse(
            reservations=reservation_reads,
            total_count=total_count,
            page=page,
            page_size=page_size
        )

    def bulk_create_reservations(self, reservations: List[ReservationCreate]) -> List[ReservationRead]:
        # 实现批量创建预约的逻辑
        pass

    def bulk_update_reservations(self, reservations: List[ReservationUpdate]) -> List[ReservationRead]:
        # 实现批量更新预约的逻辑
        pass

    def generate_check_in_token(self, reservation_id: int) -> Dict[str, str]:
        reservation = self._get_reservation(reservation_id)
        self._validate_reservation_for_check_in(reservation)

        now = datetime.utcnow()
        payload = {
            "reservation_id": reservation_id,
            "user_id": reservation.user_id,
            "exp": now + timedelta(minutes=settings.CHECK_IN_TOKEN_EXPIRY_MINUTES),
            "iat": now
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return {
            "token": token,
            "expires_at": (now + timedelta(minutes=settings.CHECK_IN_TOKEN_EXPIRY_MINUTES)).isoformat()
        }

    @staticmethod
    def verify_check_in_token(token: str) -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            reservation_id = payload.get("reservation_id")
            if not reservation_id:
                raise InvalidCheckInTimeError("Invalid token")
            return reservation_id
        except jwt.ExpiredSignatureError:
            raise InvalidCheckInTimeError("Token has expired")
        except jwt.InvalidTokenError:
            raise InvalidCheckInTimeError("Invalid token")

    def check_in(self, reservation_id: int) -> Reservation:
        reservation = self._get_reservation(reservation_id)
        self._validate_reservation_for_check_in(reservation)

        try:
            reservation.status = ReservationStatus.CHECKED_IN
            reservation.checked_in_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(reservation)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to check in: {str(e)}")
            raise

        return reservation

    @staticmethod
    def _validate_reservation_for_check_in(reservation: Reservation) -> None:
        if reservation.status != ReservationStatus.CONFIRMED:
            raise InvalidReservationStatusError("Only confirmed reservations can be checked in")

        now = datetime.utcnow()
        reservation_start = datetime.combine(reservation.date, reservation.actual_start_time)
        time_diff = abs((now - reservation_start).total_seconds() / 60)

        if time_diff > settings.CHECK_IN_TIME_WINDOW_MINUTES:
            raise InvalidCheckInTimeError("Check-in is only allowed within the specified time window")

    def _get_reservation(self, reservation_id: int) -> Reservation:
        reservation = (
            self.db.query(Reservation)
            .options(
                joinedload(Reservation.venue_available_time_slot)
                .joinedload(VenueAvailableTimeSlot.venue)
                .joinedload(Venue.sport_venue)
            )
            .filter(Reservation.id == reservation_id)
            .first()
        )

        if not reservation:
            raise ReservationNotFoundError(f"Reservation with id {reservation_id} not found")

        return reservation
