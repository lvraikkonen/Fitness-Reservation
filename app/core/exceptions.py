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


class SportVenueNotFoundError(VenueException):
    """Raised when a sport venue is not found"""
    def __init__(self, message: str = "Sport venue not found"):
        super().__init__(message, status_code=404)


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
