from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from app.models.user import User
from app.models.user_activity import UserActivity
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.reservation_rules import ReservationRules
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.reservation import Reservation, ReservationStatus
from app.models.venue import Venue
from app.models.sport_venue import SportVenue
from app.schemas.user import UserDashboardResponse, UpcomingReservation, RecentActivity, RecommendedVenue

from app.schemas.reservation import PaginatedReservationResponse
from app.services.reservation_service import ReservationService
from app.core.security import (get_password_hash, verify_password,
                               create_password_reset_token, verify_password_reset_token)
# from app.services.log_services import log_operation
from app.core.config import settings, get_logger
from app.utils.email import send_email_async
from app.utils.templates import get_notification_template
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError, ValidationError, AuthenticationError

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: Optional[int] = None, username: Optional[str] = None, email: Optional[str] = None) -> User:
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
        elif username:
            user = self.db.query(User).filter(User.username == username).first()
        elif email:
            user = self.db.query(User).filter(User.email == email).first()
        else:
            raise ValueError("Either user_id, username or email must be provided")

        if not user:
            raise UserNotFoundError("User not found")
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username,
                email=user.email,
                password=hashed_password,
                phone=user.phone,
                role=user.role,
                is_leader=user.is_leader,
                full_name=user.full_name,
                department=user.department,
                preferred_sports=user.preferred_sports,
                preferred_time=user.preferred_time
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"New user created: {db_user.username}")
            return UserResponse.from_orm(db_user)
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Attempt to create duplicate user: {user.username}")
            raise UserAlreadyExistsError("Username or email already registered!")

    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.get_user(user_id=user_id)
        update_data = user.dict(exclude_unset=True)

        # Check if email is being updated and if it's already in use
        if 'email' in update_data:
            existing_user = self.db.query(User).filter(User.email == update_data['email']).first()
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsError("Email already in use")

        for key, value in update_data.items():
            setattr(db_user, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User updated: {db_user.username}")
            return db_user
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Failed to update user: {db_user.username}")
            raise ValidationError("Failed to update user")

    def authenticate_user(self, username: str, password: str) -> User:
        try:
            user = self.get_user(username=username)
            if not verify_password(password, user.password):
                raise AuthenticationError("Incorrect username or password")
            logger.info(f"User authenticated: {user.username}")
            return user
        except UserNotFoundError:
            raise AuthenticationError("Incorrect username or password")

    def delete_user(self, user_id: int):
        db_user = self.get_user(user_id=user_id)
        self.db.delete(db_user)
        self.db.commit()
        logger.info(f"User deleted: {db_user.username}")

    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    @staticmethod
    def create_password_reset_token(user_id: int) -> str:
        token = create_password_reset_token(user_id)
        reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        return reset_link

    @staticmethod
    async def send_password_reset_email(user: User, reset_link: str) -> bool:
        subject = "Password Reset Request"
        body = get_notification_template("reset_password", {
            "username": user.username,
            "reset_link": reset_link
        })

        try:
            await send_email_async(user.email, subject, body)
            logger.info(f"Password reset email sent to: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False

    async def request_password_reset(self, email: str) -> bool:
        try:
            user = self.get_user_by_email(email)
            reset_link = UserService.create_password_reset_token(user.id)
            success = await UserService.send_password_reset_email(user, reset_link)
            if success:
                logger.info(f"Password reset requested for user: {user.username}")
            return success
        except UserNotFoundError:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return False

    def reset_password(self, token: str, new_password: str) -> bool:
        user_id = verify_password_reset_token(token)
        if not user_id:
            logger.warning("Invalid password reset token")
            return False

        try:
            user = self.get_user(user_id=user_id)
            user.password = get_password_hash(new_password)
            self.db.commit()
            logger.info(f"Password reset successful for user: {user.username}")
            return True
        except UserNotFoundError:
            logger.warning(f"Password reset failed for non-existent user ID: {user_id}")
            return False

    def update_user_avatar(self, user_id: int, avatar_url: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")
        user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        return user

    def check_rate_limit(self, user_id: int, action: str) -> None:
        # Implement rate limiting logic here
        # For example, check the number of actions performed by the user in the last hour
        # If it exceeds a certain threshold, raise RateLimitExceededError
        pass

    def get_user_reservation_history(
            self,
            user_id: int,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            page: int = 1,
            page_size: int = 20
    ) -> PaginatedReservationResponse:
        """
        获取用户的预约历史。

        这个方法是对 ReservationService.get_user_reservation_history 的包装。
        它允许在 UserService 中访问用户的预约历史，同时保持了业务逻辑的分离。

            参数:
            - user_id: 用户ID
            - start_date: 开始日期（可选）
            - end_date: 结束日期（可选）
            - page: 页码
            - page_size: 每页数量

        返回:
        - PaginatedReservationResponse: 包含分页的预约历史记录
        """
        # 首先检查用户是否存在
        user = self.get_user(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        reservation_service = ReservationService(self.db)
        return reservation_service.get_user_reservation_history(
            user_id, start_date, end_date, page, page_size
        )

    def get_upcoming_reservations(self, user_id: int, limit: int=3) -> List[UpcomingReservation]:
        current_datetime = datetime.now()
        upcoming_reservations = (
            self.db.query(Reservation)
            .join(Reservation.venue_available_time_slot)
            .join(Venue)
            .join(SportVenue)
            .filter(
                Reservation.user_id == user_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED]),
                or_(
                    VenueAvailableTimeSlot.date > current_datetime.date(),
                    and_(
                        VenueAvailableTimeSlot.date == current_datetime.date(),
                        VenueAvailableTimeSlot.start_time >= current_datetime.time()
                    )
                )
            )
            .order_by(VenueAvailableTimeSlot.date, VenueAvailableTimeSlot.start_time)
            .limit(limit)
        )

        # logger.debug(f"SQL Query: {upcoming_reservations.statement.compile(compile_kwargs={'literal_binds': True})}")
        result = upcoming_reservations.all()
        # logger.debug(f"Query result: {result}")

        return [
            UpcomingReservation(
                id=res.id,
                venue_name=res.venue_available_time_slot.venue.name,
                sport_venue_name=res.venue_available_time_slot.venue.sport_venue.name,
                date=res.venue_available_time_slot.date,
                start_time=res.venue_available_time_slot.start_time,
                end_time=res.venue_available_time_slot.end_time,
                status=res.status
            ) for res in result
        ]

    def get_recent_activities(self, user_id: int, limit: int = 5) -> List[RecentActivity]:
        VAS = aliased(VenueAvailableTimeSlot)

        activities_query = (
            self.db.query(
                UserActivity.id,
                UserActivity.activity_type,
                UserActivity.timestamp,
                func.coalesce(Venue.name, "N/A").label('venue_name'),
                func.coalesce(SportVenue.name, "N/A").label('sport_venue_name'),
                VAS.date,
                VAS.start_time,
                VAS.end_time,
                Reservation.status
            )
            .outerjoin(UserActivity.reservation)
            .outerjoin(UserActivity.venue)
            .outerjoin(Venue.sport_venue)
            .outerjoin(Reservation.venue_available_time_slot.of_type(VAS))
            .filter(UserActivity.user_id == user_id)
            .order_by(UserActivity.timestamp.desc())
            .limit(limit)
        )

        results = activities_query.all()
        return [
            RecentActivity(
                id=result.id,
                activity_type=result.activity_type,
                timestamp=result.timestamp,
                venue_name=result.venue_name,
                sport_venue_name=result.sport_venue_name,
                date=result.date,
                start_time=result.start_time,
                end_time=result.end_time,
                status=result.status
            ) for result in results
        ]

    def get_recommended_venues(self, user: User, limit: int = 3) -> List[RecommendedVenue]:
        logger.debug(f"User preferred sports: {user.preferred_sports}")

        base_query = self.db.query(Venue).join(SportVenue)

        if user.preferred_sports:
            preferred_sports = [sport.strip() for sport in user.preferred_sports.split(',')]
            logger.debug(f"Preferred sports list: {preferred_sports}")

            # 构建 LIKE 条件
            like_conditions = []
            for sport in preferred_sports:
                like_conditions.extend([
                    Venue.name.ilike(f"%{sport}%"),
                    Venue.sport_type.ilike(f"%{sport}%"),
                    Venue.description.ilike(f"%{sport}%"),
                    SportVenue.name.ilike(f"%{sport}%")
                ])

            # 先查询符合条件的场地
            preferred_query = base_query.filter(or_(*like_conditions))
            preferred_venues = preferred_query.order_by(func.random()).limit(limit).all()

            logger.debug(f"Preferred venues count: {len(preferred_venues)}")

            # 如果符合条件的场地不足，补充其他场地
            if len(preferred_venues) < limit:
                remaining_limit = limit - len(preferred_venues)
                other_venues = base_query.filter(~Venue.id.in_([v.id for v in preferred_venues])) \
                    .order_by(func.random()) \
                    .limit(remaining_limit) \
                    .all()
                recommended_venues = preferred_venues + other_venues
            else:
                recommended_venues = preferred_venues
        else:
            # 如果用户没有偏好，随机选择场地
            recommended_venues = base_query.order_by(func.random()).limit(limit).all()

        if not recommended_venues:
            logger.warning("No recommended venues found")
            return []

        return [
            RecommendedVenue(
                id=venue.id,
                name=venue.name,
                sport_venue_name=venue.sport_venue.name
            ) for venue in recommended_venues
        ]

    def get_monthly_reservation_info(self, user_id: int, user_role: str) -> tuple:
        current_date = datetime.now()
        start_of_month = current_date.replace(day=1)

        monthly_reservation_count = (
            self.db.query(func.count(Reservation.id))
            .filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= start_of_month,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
            )
            .scalar()
        )

        monthly_reservation_limit = (
            self.db.query(ReservationRules.max_monthly_reservations)
            .filter(ReservationRules.user_role == user_role)
            .order_by(ReservationRules.id.desc())
            .first()
        )

        if monthly_reservation_limit is None:
            monthly_reservation_limit = 20
        else:
            monthly_reservation_limit = monthly_reservation_limit[0]

        return monthly_reservation_count, monthly_reservation_limit

    def get_dashboard_data(self, user_id: int) -> UserDashboardResponse:
        user = self.get_user(user_id=user_id)

        upcoming_reservations = self.get_upcoming_reservations(user_id)
        recent_activities = self.get_recent_activities(user_id)
        recommended_venues = self.get_recommended_venues(user)
        monthly_reservation_count, monthly_reservation_limit = self.get_monthly_reservation_info(user_id, user.role)

        return UserDashboardResponse(
            username=user.username,
            upcoming_reservations=upcoming_reservations,
            recent_activities=recent_activities,
            recommended_venues=recommended_venues,
            monthly_reservation_count=monthly_reservation_count,
            monthly_reservation_limit=monthly_reservation_limit
        )
