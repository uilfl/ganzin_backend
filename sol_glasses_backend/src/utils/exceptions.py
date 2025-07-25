#!/usr/bin/env python3
"""
Custom exceptions for Sol Glasses Backend
Comprehensive error handling with proper HTTP status codes and logging
"""

from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Sol SDK related errors
    SOL_SDK_NOT_AVAILABLE = "SOL_SDK_NOT_AVAILABLE"
    SOL_GLASSES_CONNECTION_FAILED = "SOL_GLASSES_CONNECTION_FAILED"
    SOL_GLASSES_TIMEOUT = "SOL_GLASSES_TIMEOUT"
    SOL_GLASSES_INVALID_RESPONSE = "SOL_GLASSES_INVALID_RESPONSE"
    
    # Database related errors
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    DATABASE_OPERATION_FAILED = "DATABASE_OPERATION_FAILED"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    
    # Processing related errors
    GAZE_PROCESSING_FAILED = "GAZE_PROCESSING_FAILED"
    INVALID_GAZE_DATA = "INVALID_GAZE_DATA"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"
    AOI_MAPPING_FAILED = "AOI_MAPPING_FAILED"
    
    # Session related errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    SESSION_ALREADY_EXISTS = "SESSION_ALREADY_EXISTS"
    INVALID_SESSION_STATE = "INVALID_SESSION_STATE"
    
    # WebSocket related errors
    WEBSOCKET_CONNECTION_FAILED = "WEBSOCKET_CONNECTION_FAILED"
    WEBSOCKET_MESSAGE_INVALID = "WEBSOCKET_MESSAGE_INVALID"
    WEBSOCKET_TIMEOUT = "WEBSOCKET_TIMEOUT"
    
    # Adaptation service errors
    ADAPTATION_RULE_FAILED = "ADAPTATION_RULE_FAILED"
    FEEDBACK_GENERATION_FAILED = "FEEDBACK_GENERATION_FAILED"
    
    # Performance related errors
    PERFORMANCE_THRESHOLD_EXCEEDED = "PERFORMANCE_THRESHOLD_EXCEEDED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Privacy/Security errors (R12)
    DATA_DELETION_FAILED = "DATA_DELETION_FAILED"
    ENCRYPTION_FAILED = "ENCRYPTION_FAILED"
    AUDIT_LOG_FAILED = "AUDIT_LOG_FAILED"

class SolGlassesException(Exception):
    """Base exception for all Sol Glasses backend errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        http_status: int = 500,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details
            }
        }
    
    def __str__(self) -> str:
        return f"{self.error_code.value}: {self.message}"

# Sol SDK related exceptions
class SolSDKException(SolGlassesException):
    """Base exception for Sol SDK related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=503, **kwargs)

class SolSDKNotAvailableError(SolSDKException):
    """Raised when Sol SDK is not available or not installed"""
    
    def __init__(self, message: str = "Sol SDK is not available"):
        super().__init__(message, ErrorCode.SOL_SDK_NOT_AVAILABLE)

class SolGlassesConnectionError(SolSDKException):
    """Raised when connection to Sol Glasses fails"""
    
    def __init__(self, message: str = "Failed to connect to Sol Glasses", **kwargs):
        super().__init__(message, ErrorCode.SOL_GLASSES_CONNECTION_FAILED, **kwargs)

class SolGlassesTimeoutError(SolSDKException):
    """Raised when Sol Glasses operation times out"""
    
    def __init__(self, message: str = "Sol Glasses operation timed out", **kwargs):
        super().__init__(message, ErrorCode.SOL_GLASSES_TIMEOUT, **kwargs)

class SolGlassesInvalidResponseError(SolSDKException):
    """Raised when Sol Glasses returns invalid response"""
    
    def __init__(self, message: str = "Invalid response from Sol Glasses", **kwargs):
        super().__init__(message, ErrorCode.SOL_GLASSES_INVALID_RESPONSE, **kwargs)

# Database related exceptions
class DatabaseException(SolGlassesException):
    """Base exception for database related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=503, **kwargs)

class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails"""
    
    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, ErrorCode.DATABASE_CONNECTION_FAILED, **kwargs)

class DatabaseOperationError(DatabaseException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, ErrorCode.DATABASE_OPERATION_FAILED, **kwargs)

class DatabaseTimeoutError(DatabaseException):
    """Raised when database operation times out"""
    
    def __init__(self, message: str = "Database operation timed out", **kwargs):
        super().__init__(message, ErrorCode.DATABASE_TIMEOUT, **kwargs)

class DataNotFoundError(DatabaseException):
    """Raised when requested data is not found"""
    
    def __init__(self, message: str = "Data not found", **kwargs):
        super().__init__(message, ErrorCode.DATA_NOT_FOUND, http_status=404, **kwargs)

# Processing related exceptions
class ProcessingException(SolGlassesException):
    """Base exception for processing related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=422, **kwargs)

class GazeProcessingError(ProcessingException):
    """Raised when gaze processing fails"""
    
    def __init__(self, message: str = "Gaze processing failed", **kwargs):
        super().__init__(message, ErrorCode.GAZE_PROCESSING_FAILED, **kwargs)

class InvalidGazeDataError(ProcessingException):
    """Raised when gaze data is invalid"""
    
    def __init__(self, message: str = "Invalid gaze data", **kwargs):
        super().__init__(message, ErrorCode.INVALID_GAZE_DATA, **kwargs)

class ProcessingTimeoutError(ProcessingException):
    """Raised when processing operation times out"""
    
    def __init__(self, message: str = "Processing operation timed out", **kwargs):
        super().__init__(message, ErrorCode.PROCESSING_TIMEOUT, **kwargs)

class AOIMappingError(ProcessingException):
    """Raised when AOI mapping fails"""
    
    def __init__(self, message: str = "AOI mapping failed", **kwargs):
        super().__init__(message, ErrorCode.AOI_MAPPING_FAILED, **kwargs)

# Session related exceptions
class SessionException(SolGlassesException):
    """Base exception for session related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=400, **kwargs)

class SessionNotFoundError(SessionException):
    """Raised when session is not found"""
    
    def __init__(self, session_id: str, **kwargs):
        message = f"Session not found: {session_id}"
        super().__init__(message, ErrorCode.SESSION_NOT_FOUND, http_status=404, **kwargs)

class SessionExpiredError(SessionException):
    """Raised when session has expired"""
    
    def __init__(self, session_id: str, **kwargs):
        message = f"Session expired: {session_id}"
        super().__init__(message, ErrorCode.SESSION_EXPIRED, http_status=410, **kwargs)

class SessionAlreadyExistsError(SessionException):
    """Raised when session already exists"""
    
    def __init__(self, session_id: str, **kwargs):
        message = f"Session already exists: {session_id}"
        super().__init__(message, ErrorCode.SESSION_ALREADY_EXISTS, http_status=409, **kwargs)

class InvalidSessionStateError(SessionException):
    """Raised when session is in invalid state"""
    
    def __init__(self, session_id: str, current_state: str, expected_state: str, **kwargs):
        message = f"Session {session_id} is in invalid state: {current_state}, expected: {expected_state}"
        super().__init__(message, ErrorCode.INVALID_SESSION_STATE, **kwargs)

# WebSocket related exceptions
class WebSocketException(SolGlassesException):
    """Base exception for WebSocket related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=400, **kwargs)

class WebSocketConnectionError(WebSocketException):
    """Raised when WebSocket connection fails"""
    
    def __init__(self, message: str = "WebSocket connection failed", **kwargs):
        super().__init__(message, ErrorCode.WEBSOCKET_CONNECTION_FAILED, **kwargs)

class WebSocketMessageInvalidError(WebSocketException):
    """Raised when WebSocket message is invalid"""
    
    def __init__(self, message: str = "Invalid WebSocket message", **kwargs):
        super().__init__(message, ErrorCode.WEBSOCKET_MESSAGE_INVALID, **kwargs)

class WebSocketTimeoutError(WebSocketException):
    """Raised when WebSocket operation times out"""
    
    def __init__(self, message: str = "WebSocket operation timed out", **kwargs):
        super().__init__(message, ErrorCode.WEBSOCKET_TIMEOUT, **kwargs)

# Adaptation service exceptions
class AdaptationException(SolGlassesException):
    """Base exception for adaptation service errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=422, **kwargs)

class AdaptationRuleError(AdaptationException):
    """Raised when adaptation rule fails"""
    
    def __init__(self, rule_id: str, message: str = None, **kwargs):
        message = message or f"Adaptation rule failed: {rule_id}"
        super().__init__(message, ErrorCode.ADAPTATION_RULE_FAILED, **kwargs)

class FeedbackGenerationError(AdaptationException):
    """Raised when feedback generation fails"""
    
    def __init__(self, message: str = "Feedback generation failed", **kwargs):
        super().__init__(message, ErrorCode.FEEDBACK_GENERATION_FAILED, **kwargs)

# Performance related exceptions
class PerformanceException(SolGlassesException):
    """Base exception for performance related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=503, **kwargs)

class PerformanceThresholdExceededError(PerformanceException):
    """Raised when performance threshold is exceeded"""
    
    def __init__(self, metric: str, threshold: float, actual: float, **kwargs):
        message = f"Performance threshold exceeded for {metric}: {actual} > {threshold}"
        super().__init__(message, ErrorCode.PERFORMANCE_THRESHOLD_EXCEEDED, **kwargs)

class RateLimitExceededError(PerformanceException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED, http_status=429, **kwargs)

# Privacy/Security exceptions (R12)
class SecurityException(SolGlassesException):
    """Base exception for security related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=500, **kwargs)

class DataDeletionError(SecurityException):
    """Raised when data deletion fails"""
    
    def __init__(self, user_id: str, message: str = None, **kwargs):
        message = message or f"Data deletion failed for user: {user_id}"
        super().__init__(message, ErrorCode.DATA_DELETION_FAILED, **kwargs)

class EncryptionError(SecurityException):
    """Raised when encryption operation fails"""
    
    def __init__(self, message: str = "Encryption operation failed", **kwargs):
        super().__init__(message, ErrorCode.ENCRYPTION_FAILED, **kwargs)

class AuditLogError(SecurityException):
    """Raised when audit logging fails"""
    
    def __init__(self, message: str = "Audit logging failed", **kwargs):
        super().__init__(message, ErrorCode.AUDIT_LOG_FAILED, **kwargs)

# Validation exceptions
class ValidationError(SolGlassesException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, http_status=422, **kwargs)
        if field:
            self.details['field'] = field

# Authentication/Authorization exceptions
class AuthenticationError(SolGlassesException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, ErrorCode.AUTHENTICATION_FAILED, http_status=401, **kwargs)

class AuthorizationError(SolGlassesException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(message, ErrorCode.AUTHORIZATION_FAILED, http_status=403, **kwargs)

# Utility functions for error handling
def handle_sol_sdk_errors(func):
    """Decorator to handle Sol SDK errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            raise SolSDKNotAvailableError(f"Sol SDK not available: {e}")
        except ConnectionError as e:
            raise SolGlassesConnectionError(f"Connection error: {e}")
        except TimeoutError as e:
            raise SolGlassesTimeoutError(f"Timeout error: {e}")
        except Exception as e:
            raise SolGlassesInvalidResponseError(f"Unexpected error: {e}")
    
    return wrapper

def handle_database_errors(func):
    """Decorator to handle database errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Connection error: {e}")
        except TimeoutError as e:
            raise DatabaseTimeoutError(f"Timeout error: {e}")
        except Exception as e:
            raise DatabaseOperationError(f"Database error: {e}")
    
    return wrapper