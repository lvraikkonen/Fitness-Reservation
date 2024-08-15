from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List, Union, Dict
from datetime import date
from app.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.models.reservation import ReservationStatus
from app.schemas.venue_available_time_slot import VenueAvailabilityRead
from app.services.venue_service import VenueService
from app.services.reservation_service import ReservationService
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationRead, \
    ReservationDetailRead, PaginatedReservationResponse, \
    RecurringReservationCreate, RecurringReservationRead, RecurringReservationUpdate, ReservationConfirmationResult
from app.schemas.reservation import VenueCalendarResponse, ConflictCheckResult
from app.schemas.waiting_list import WaitingListRead
from app.core.exceptions import ReservationException, ReservationNotFoundError, InvalidReservationStatusError, \
    InvalidCheckInTimeError
from app.core.exceptions import ReservationConflictError, DatabaseError
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/reservations", response_model=Union[List[ReservationRead], List[WaitingListRead]],
             status_code=status.HTTP_201_CREATED)
def create_reservation(
        reservation: ReservationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Create a new reservation or add to waiting list if there's a conflict.

    This endpoint creates a new reservation for the current user. If there's a conflict
    (e.g., the time slot is already fully booked), it adds the user to the waiting list.
    """
    logger.info(f"Received reservation data: {reservation}")
    reservation_service = ReservationService(db)
    try:
        # Ensure the user_id in the reservation matches the current user
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User ID mismatch")

        result = reservation_service.create_reservation(reservation)
        logger.info(f"Reservation created for user {current_user.id}: {result}")
        return result
    except ReservationConflictError as e:
        logger.warning(f"Reservation conflict for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error during reservation creation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
    except Exception as e:
        logger.error(f"Unexpected error during reservation creation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reservations/{reservation_id}", response_model=ReservationDetailRead)
def get_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Retrieve details of a specific reservation.

    Args:
        reservation_id (int): The ID of the reservation to retrieve.
        current_user (User): The authenticated user making the request.
        db (Session): The database session.
    """
    reservation_service = ReservationService(db)
    reservation = reservation_service.get_reservation(reservation_id)

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # 检查用户权限（例如，只有预约的用户或管理员可以查看）
    if reservation.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this reservation")

    return reservation


@router.get("/reservations", response_model=PaginatedReservationResponse)
def get_all_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all reservations with pagination.

    Args:
        skip (int): The number of reservations to skip (for pagination).
        limit (int): The maximum number of reservations to return (for pagination).
        current_user (User): The authenticated user making the request.
        db (Session): The database session.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can view all reservations")

    reservation_service = ReservationService(db)
    reservations, total_count = reservation_service.get_all_reservations(skip=skip, limit=limit)

    return PaginatedReservationResponse(
        reservations=reservations,
        total_count=total_count,
        page=skip // limit + 1,
        page_size=limit
    )


@router.put("/reservations/{reservation_id}", response_model=ReservationRead)
def update_reservation(
        reservation_id: int,
        reservation: ReservationUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        # 检查用户是否有权限更新这个预约
        original_reservation = reservation_service.get_reservation(reservation_id)
        if original_reservation.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to update this reservation")

        updated_reservation = reservation_service.update_reservation(reservation_id, reservation)
        return updated_reservation
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReservationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        reservation_service.cancel_reservation(reservation_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

    return {"message": "Reservation cancelled successfully"}


@router.post("/reservations/{reservation_id}/confirm", response_model=ReservationConfirmationResult)
def confirm_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        return reservation_service.confirm_reservation(reservation_id)
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReservationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/venues/{venue_id}/waiting-list", response_model=List[WaitingListRead])
def get_waiting_list(
        venue_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.get_waiting_list(venue_id)


@router.post("/reservations/check-conflict", response_model=ConflictCheckResult)
def check_reservation_conflict(
        reservation: ReservationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        # Ensure the user_id in the reservation matches the current user
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User ID mismatch")

        conflict_result = reservation_service.check_reservation_conflict(reservation)
        return conflict_result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred: {str(e)}")


@router.get("/venues/{venue_id}/calendar", response_model=VenueCalendarResponse)
def get_venue_calendar(
    venue_id: int,
    start_date: Optional[date] = Query(None, description="Start date for calendar data"),
    end_date: Optional[date] = Query(None, description="End date for calendar data"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
        Retrieve the calendar data for a specific venue.

        This endpoint returns paginated calendar data for the specified venue,
        including time slots and their reservations. It supports optional date range filtering.
    """
    try:
        reservation_service = ReservationService(db)
        calendar_data = reservation_service.get_venue_calendar(
            venue_id, start_date, end_date, page, page_size
        )
        return calendar_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving calendar data")


@router.get("/user-reservations", response_model=PaginatedReservationResponse)
def get_user_reservations(
    user_id: int,
    venue_id: Optional[int] = None,
    status: Optional[ReservationStatus] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated reservations for a specific user.

    This endpoint returns a paginated list of reservations for the specified user.
    It supports optional filtering by venue and reservation status.
    """
    reservation_service = ReservationService(db)
    try:
        return reservation_service.get_user_reservations(user_id, venue_id, status, page, page_size)
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReservationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# 周期性预约
@router.post("/recurring-reservations", response_model=RecurringReservationRead)
def create_recurring_reservation(
    recurring_reservation: RecurringReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.create_recurring_reservation(recurring_reservation, current_user.id)


@router.get("/recurring-reservations/{recurring_id}", response_model=RecurringReservationRead)
def get_recurring_reservation(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.get_recurring_reservation(recurring_id, current_user.id)


@router.put("/recurring-reservations/{recurring_id}", response_model=RecurringReservationRead)
def update_recurring_reservation(
    recurring_id: int,
    recurring_reservation: RecurringReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.update_recurring_reservation(recurring_id, recurring_reservation, current_user.id)


@router.delete("/recurring-reservations/{recurring_id}", status_code=204)
def delete_recurring_reservation(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    reservation_service.delete_recurring_reservation(recurring_id, current_user.id)


# 用户预约历史
@router.get("/users/{user_id}/reservation-history", response_model=PaginatedReservationResponse)
def get_user_reservation_history(
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's history")

    reservation_service = ReservationService(db)
    return reservation_service.get_user_reservation_history(user_id, start_date, end_date, page, page_size)


# 场地可用性检查
@router.get("/venues/{venue_id}/availability", response_model=List[VenueAvailabilityRead])
def check_venue_availability(
    venue_id: int,
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    try:
        availability = venue_service.check_venue_availability(venue_id, start_date, end_date)
        return availability
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 记录错误
        logger.error(f"Error checking venue availability: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while checking venue availability")


# 批量预约操作（适用于管理员）
@router.post("/reservations/bulk", response_model=List[ReservationRead])
def bulk_create_reservations(
    reservations: List[ReservationCreate],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.bulk_create_reservations(reservations)


@router.put("/reservations/bulk", response_model=List[ReservationRead])
def bulk_update_reservations(
    reservations: List[ReservationUpdate],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.bulk_update_reservations(reservations)


@router.post("/reservations/{reservation_id}/check-in-token", response_model=Dict[str, str])
def generate_check_in_token(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        token_info = reservation_service.generate_check_in_token(reservation_id)
        return token_info
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InvalidReservationStatusError, InvalidCheckInTimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/check-in", response_model=ReservationRead)
def check_in(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        reservation_id = ReservationService.verify_check_in_token(token)
        checked_in_reservation = reservation_service.check_in(reservation_id)
        return ReservationRead.from_orm(checked_in_reservation)
    except InvalidCheckInTimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InvalidReservationStatusError, InvalidCheckInTimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/reservations/{reservation_id}/check-in", response_model=ReservationRead)
def direct_check_in(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        checked_in_reservation = reservation_service.check_in(reservation_id)
        return ReservationRead.from_orm(checked_in_reservation)
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InvalidReservationStatusError, InvalidCheckInTimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
