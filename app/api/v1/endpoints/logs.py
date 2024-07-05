from fastapi import APIRouter, Depends, Query
from datetime import datetime
from app.models.user import User
from app.services.log_services import get_user_logs, get_all_logs
from app.deps import get_current_user, get_current_admin

router = APIRouter()


@router.get("/me")
def read_user_logs(
    current_user: User = Depends(get_current_user),
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    operation: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    logs = get_user_logs(current_user.id, start_time, end_time, operation, skip, limit)
    return [log.to_mongo() for log in logs]


@router.get("/user/{user_id}")
def read_user_logs_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    operation: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    logs = get_user_logs(user_id, start_time, end_time, operation, skip, limit)
    return [log.to_mongo() for log in logs]


@router.get("/")
def read_all_logs(
    current_user: User = Depends(get_current_admin),
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    operation: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    logs = get_all_logs(start_time, end_time, operation, skip, limit)
    return [log.to_mongo() for log in logs]
