class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ReservationException(BaseAPIException):
    """Base exception for reservation related errors"""
    def __init__(self, message: str = "An error occurred with the reservation", status_code: int = 400):
        super().__init__(message, status_code)


class ReservationConflictError(ReservationException):
    """Exception raised when there's a conflict in reservation"""
    def __init__(self, message: str = "Reservation conflict occurred"):
        super().__init__(message, status_code=409)


class DatabaseError(BaseAPIException):
    """Exception raised when there's a database-related error"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status_code=500)


class NotFoundError(BaseAPIException):
    """Exception raised when a requested resource is not found"""
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(BaseAPIException):
    """Exception raised when there's a validation error"""
    def __init__(self, message: str = "Validation error occurred"):
        super().__init__(message, status_code=400)


class AuthenticationError(BaseAPIException):
    """Exception raised when there's an authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseAPIException):
    """Exception raised when there's an authorization error"""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, status_code=403)


class ReservationNotFoundError(ReservationException):
    """Raised when a reservation is not found"""
    def __init__(self, message: str = "Reservation not found"):
        super().__init__(message, status_code=404)


class ReservationCreateError(ReservationException):
    """Raised when there's an error creating a reservation"""
    def __init__(self, message: str = "Error creating reservation"):
        super().__init__(message, status_code=400)