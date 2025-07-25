#!/usr/bin/env python3
"""
Custom exceptions for Sol Glasses Backend Test
Simplified exception handling for backend test functionality
"""

from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
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
    
    # Processing related errors
    GAZE_PROCESSING_FAILED = "GAZE_PROCESSING_FAILED"
    INVALID_GAZE_DATA = "INVALID_GAZE_DATA"
    
    # Session related errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    
    # WebSocket related errors
    WEBSOCKET_CONNECTION_FAILED = "WEBSOCKET_CONNECTION_FAILED"
    WEBSOCKET_MESSAGE_INVALID = "WEBSOCKET_MESSAGE_INVALID"

class SolGlassesException(Exception):
    """Base exception for all Sol Glasses backend errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        http_status: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
    
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

# Processing related exceptions
class ProcessingException(SolGlassesException):
    """Base exception for processing related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=422, **kwargs)

class InvalidGazeDataError(ProcessingException):
    """Raised when gaze data is invalid"""
    
    def __init__(self, message: str = "Invalid gaze data", **kwargs):
        super().__init__(message, ErrorCode.INVALID_GAZE_DATA, **kwargs)

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

# WebSocket related exceptions
class WebSocketException(SolGlassesException):
    """Base exception for WebSocket related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(message, error_code, http_status=400, **kwargs)

class WebSocketMessageInvalidError(WebSocketException):
    """Raised when WebSocket message is invalid"""
    
    def __init__(self, message: str = "Invalid WebSocket message", **kwargs):
        super().__init__(message, ErrorCode.WEBSOCKET_MESSAGE_INVALID, **kwargs)

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
            raise SolGlassesConnectionError(f"Unexpected error: {e}")
    
    return wrapper