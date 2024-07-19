from fastapi import HTTPException


class BaseAPIException(HTTPException):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)


class DatabaseError(BaseAPIException):
    """Exception raised when there's a database-related error"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status_code=500)


class ValidationError(BaseAPIException):
    """Exception raised when there's a validation error"""
    def __init__(self, message: str = "Validation error occurred"):
        super().__init__(message, status_code=400)


class NotFoundError(BaseAPIException):
    """Exception raised when a requested resource is not found"""
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message, status_code=404)


class AuthenticationError(BaseAPIException):
    """Exception raised when there's an authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseAPIException):
    """Exception raised when there's an authorization error"""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, status_code=403)


class ConfigurationError(BaseAPIException):
    """Exception raised when there's a configuration error"""
    def __init__(self, message: str = "Configuration error occurred"):
        super().__init__(message, status_code=500)


class ExternalServiceError(BaseAPIException):
    """Exception raised when there's an error with an external service"""
    def __init__(self, message: str = "External service error occurred"):
        super().__init__(message, status_code=503)


# User-specific exceptions
class UserException(BaseAPIException):
    """Base exception for user-related errors"""
    def __init__(self, message: str = "An error occurred with the user", status_code: int = 400):
        super().__init__(message, status_code)


class UserNotFoundError(UserException):
    """Raised when a user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)


class UserAlreadyExistsError(UserException):
    """Raised when attempting to create a user that already exists"""
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, status_code=409)


class InvalidCredentialsError(UserException):
    """Raised when provided credentials are invalid"""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class PasswordResetError(UserException):
    """Raised when there's an error with password reset"""
    def __init__(self, message: str = "Error occurred during password reset"):
        super().__init__(message, status_code=400)


class RateLimitExceededError(BaseAPIException):
    """Raised when a rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


# Reservation Exceptions
class ReservationException(BaseAPIException):
    """Base exception for reservation related errors"""
    def __init__(self, message: str = "An error occurred with the reservation", status_code: int = 400):
        super().__init__(message, status_code)


class ReservationNotFoundError(ReservationException):
    """Raised when a reservation is not found"""
    def __init__(self, message: str = "Reservation not found"):
        super().__init__(message, status_code=404)


class ReservationConflictError(ReservationException):
    """Exception raised when there's a conflict in reservation"""
    def __init__(self, message: str = "Reservation conflict occurred"):
        super().__init__(message, status_code=409)


class ReservationCreateError(ReservationException):
    """Raised when there's an error creating a reservation"""
    def __init__(self, message: str = "Error creating reservation"):
        super().__init__(message, status_code=400)


class SportVenueException(BaseAPIException):
    """Base exception for sport venue-related errors"""
    def __init__(self, message: str = "An error occurred with the sport venue", status_code: int = 400):
        super().__init__(message, status_code)


class SportVenueNotFoundError(SportVenueException):
    """Raised when a sport venue is not found"""
    def __init__(self, message: str = "Sport venue not found"):
        super().__init__(message, status_code=404)


class SportVenueCreateError(SportVenueException):
    """Raised when there's an error creating a sport venue"""
    def __init__(self, message: str = "Error creating sport venue"):
        super().__init__(message, status_code=400)


class SportVenueUpdateError(SportVenueException):
    """Raised when there's an error updating a sport venue"""
    def __init__(self, message: str = "Error updating sport venue"):
        super().__init__(message, status_code=400)


class SportVenueDeleteError(SportVenueException):
    """Raised when there's an error deleting a sport venue"""
    def __init__(self, message: str = "Error deleting sport venue"):
        super().__init__(message, status_code=400)


class SportVenueValidationError(SportVenueException):
    """Raised when there's a validation error specific to sport venue"""
    def __init__(self, message: str = "Sport venue validation error"):
        super().__init__(message, status_code=422)


class SportVenueDuplicateError(SportVenueException):
    """Raised when attempting to create a duplicate sport venue"""
    def __init__(self, message: str = "Sport venue with this name already exists"):
        super().__init__(message, status_code=409)


class SportVenueCapacityError(SportVenueException):
    """Raised when there's an issue with sport venue capacity"""
    def __init__(self, message: str = "Invalid sport venue capacity"):
        super().__init__(message, status_code=400)


class SportVenueOperationError(SportVenueException):
    """Raised when there's an error performing an operation on a sport venue"""
    def __init__(self, message: str = "Error performing operation on sport venue"):
        super().__init__(message, status_code=400)


# Venue Exceptions
class VenueException(BaseAPIException):
    """Base exception for venue-related errors"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)


class VenueNotFoundError(VenueException):
    """Raised when a venue is not found"""
    def __init__(self, message: str = "Venue not found"):
        super().__init__(message, status_code=404)


class VenueCreateError(VenueException):
    """Raised when there's an error creating a venue"""
    def __init__(self, message: str = "Error creating venue"):
        super().__init__(message, status_code=400)


class VenueUpdateError(VenueException):
    """Raised when there's an error updating a venue"""
    def __init__(self, message: str = "Error updating venue"):
        super().__init__(message, status_code=400)


class VenueDeleteError(VenueException):
    """Raised when there's an error deleting a venue"""
    def __init__(self, message: str = "Error deleting venue"):
        super().__init__(message, status_code=400)


class VenueStatusUpdateError(VenueException):
    """Raised when there's an error updating venue status"""
    def __init__(self, message: str = "Error updating venue status"):
        super().__init__(message, status_code=400)


# TimeSlot Exceptions
class TimeSlotException(BaseAPIException):
    """Base exception for time slot related errors"""
    def __init__(self, message: str = "An error occurred with the time slot", status_code: int = 400):
        super().__init__(message, status_code)


class TimeSlotExistsError(TimeSlotException):
    """Raised when attempting to create a time slot that already exists"""
    def __init__(self, message: str = "Time slot already exists"):
        super().__init__(message, status_code=409)


class TimeSlotNotFoundError(TimeSlotException):
    """Raised when a time slot is not found"""
    def __init__(self, message: str = "Time slot not found"):
        super().__init__(message, status_code=404)


class CapacityExceededError(TimeSlotException):
    """Raised when time slot capacity exceeds venue capacity"""
    def __init__(self, message: str = "Time slot capacity exceeded venue capacity"):
        super().__init__(message, status_code=400)


class TimeSlotConflictError(TimeSlotException):
    """Raised when there's a conflict between time slots"""
    def __init__(self, message: str = "Time slot conflict occurred"):
        super().__init__(message, status_code=409)


# User Exceptions
class UserException(BaseAPIException):
    """Base exception for user-related errors"""
    def __init__(self, message: str = "An error occurred with the user", status_code: int = 400):
        super().__init__(message, status_code)


class NotificationException(BaseAPIException):
    """Base exception for notification-related errors"""
    def __init__(self, message: str = "An error occurred with the notification", status_code: int = 400):
        super().__init__(message, status_code)


# notification related
class NotificationNotFoundError(NotificationException):
    """Raised when a notification is not found"""
    def __init__(self, message: str = "Notification not found"):
        super().__init__(message, status_code=404)


class NotificationCreateError(NotificationException):
    """Raised when there's an error creating a notification"""
    def __init__(self, message: str = "Error creating notification"):
        super().__init__(message, status_code=400)


class NotificationUpdateError(NotificationException):
    """Raised when there's an error updating a notification"""
    def __init__(self, message: str = "Error updating notification"):
        super().__init__(message, status_code=400)


class NotificationDeleteError(NotificationException):
    """Raised when there's an error deleting a notification"""
    def __init__(self, message: str = "Error deleting notification"):
        super().__init__(message, status_code=400)


class WaitingListException(BaseAPIException):
    """等待列表相关异常的基类"""
    def __init__(self, message: str = "An error occurred with the waiting list", status_code: int = 400):
        super().__init__(message, status_code)


# Waiting List related
class WaitingListEntryNotFoundError(WaitingListException):
    """当请求的等待列表条目不存在时抛出"""
    def __init__(self, message: str = "Waiting list entry not found"):
        super().__init__(message, status_code=404)


class WaitingListEntryExistsError(WaitingListException):
    """当尝试创建已存在的等待列表条目时抛出"""
    def __init__(self, message: str = "Waiting list entry already exists"):
        super().__init__(message, status_code=409)


class WaitingListFullError(WaitingListException):
    """当等待列表已满时抛出"""
    def __init__(self, message: str = "Waiting list is full"):
        super().__init__(message, status_code=400)


class WaitingListOperationError(WaitingListException):
    """当等待列表操作失败时抛出"""
    def __init__(self, message: str = "Failed to perform operation on waiting list"):
        super().__init__(message, status_code=400)


class InvalidWaitingListEntryError(WaitingListException):
    """当提供的等待列表条目数据无效时抛出"""
    def __init__(self, message: str = "Invalid waiting list entry data"):
        super().__init__(message, status_code=400)


class WaitingListAccessDeniedError(WaitingListException):
    """当用户没有权限访问或修改等待列表时抛出"""
    def __init__(self, message: str = "Access to waiting list denied"):
        super().__init__(message, status_code=403)


class WaitingListExpiredError(WaitingListException):
    """当等待列表条目已过期时抛出"""
    def __init__(self, message: str = "Waiting list entry has expired"):
        super().__init__(message, status_code=410)


# feedback related
class FeedbackException(BaseAPIException):
    """Base exception for feedback-related errors"""
    def __init__(self, message: str = "An error occurred with the feedback", status_code: int = 400):
        super().__init__(message, status_code)


class FeedbackNotFoundError(FeedbackException):
    """Raised when a feedback is not found"""
    def __init__(self, message: str = "Feedback not found"):
        super().__init__(message, status_code=404)


class FeedbackCreateError(FeedbackException):
    """Raised when there's an error creating a feedback"""
    def __init__(self, message: str = "Error creating feedback"):
        super().__init__(message, status_code=400)


class FeedbackUpdateError(FeedbackException):
    """Raised when there's an error updating a feedback"""
    def __init__(self, message: str = "Error updating feedback"):
        super().__init__(message, status_code=400)


class FeedbackDeleteError(FeedbackException):
    """Raised when there's an error deleting a feedback"""
    def __init__(self, message: str = "Error deleting feedback"):
        super().__init__(message, status_code=400)


class FeedbackReplyError(FeedbackException):
    """Raised when there's an error replying to a feedback"""
    def __init__(self, message: str = "Error replying to feedback"):
        super().__init__(message, status_code=400)


class FeedbackValidationError(ValidationError):
    """Raised when there's a validation error specific to feedback"""
    def __init__(self, message: str = "Feedback validation error"):
        super().__init__(message)


class RatingOutOfRangeError(FeedbackValidationError):
    """Raised when the provided rating is out of the allowed range"""
    def __init__(self, message: str = "Rating must be between 1 and 5"):
        super().__init__(message)


class FeedbackContentTooShortError(FeedbackValidationError):
    """Raised when the feedback content is too short"""
    def __init__(self, message: str = "Feedback content must be at least 10 characters long"):
        super().__init__(message)
