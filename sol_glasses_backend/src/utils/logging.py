#!/usr/bin/env python3
"""
Production-ready logging configuration for Sol Glasses Backend
Structured logging with performance monitoring and audit trails
"""

import os
import sys
import logging
import logging.config
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory

# Import config with fallback for circular imports
try:
    from .config import config, is_production, is_development
except ImportError:
    # Fallback configuration
    config = None
    def is_production(): return os.getenv('ENVIRONMENT') == 'production'
    def is_development(): return os.getenv('ENVIRONMENT', 'development') == 'development'

def setup_logging(
    log_level: Optional[str] = None,
    enable_json: Optional[bool] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup comprehensive logging for Sol Glasses Backend
    
    Features:
    - Structured logging with contextual information
    - JSON output for production (for log aggregation)
    - Human-readable output for development
    - Performance monitoring integration
    - Audit trail for R12 compliance
    """
    
    # Determine configuration
    if config:
        log_level = log_level or config.server.log_level
        enable_json = enable_json if enable_json is not None else is_production()
    else:
        log_level = log_level or os.getenv('LOG_LEVEL', 'info')
        enable_json = enable_json if enable_json is not None else is_production()
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure structlog processors
    processors = [
        # Add timestamp
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="ISO"),
        # Add request ID and session context
        add_request_context,
        # Performance monitoring
        add_performance_context,
    ]
    
    if enable_json:
        # Production: JSON output for log aggregation
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])
        formatter_class = 'logging.Formatter'
        format_string = '%(message)s'
    else:
        # Development: Human-readable output
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
        formatter_class = 'logging.Formatter'
        format_string = '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create logging configuration
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                '()': formatter_class,
                'format': format_string,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': numeric_level,
                'formatter': 'standard',
                'stream': sys.stdout
            },
        },
        'loggers': {
            '': {  # Root logger
                'level': numeric_level,
                'handlers': ['console'],
                'propagate': False
            },
            'sol_glasses': {  # Our application logger
                'level': numeric_level,
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO' if is_development() else 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'fastapi': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
        }
    }
    
    # Add file handler if specified
    if log_file:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        log_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': numeric_level,
            'formatter': 'standard',
            'filename': str(log_file_path),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        
        # Add file handler to all loggers
        for logger_config in log_config['loggers'].values():
            logger_config['handlers'].append('file')
    
    # Apply logging configuration
    logging.config.dictConfig(log_config)
    
    # Log startup message
    logger = get_logger('sol_glasses.startup')
    logger.info(
        "Logging configured",
        log_level=log_level,
        json_output=enable_json,
        file_output=log_file is not None,
        environment=os.getenv('ENVIRONMENT', 'development')
    )

def add_request_context(logger, method_name, event_dict):
    """Add request context to log entries"""
    # Add request ID if available (set by middleware)
    request_id = getattr(logger, '_request_id', None)
    if request_id:
        event_dict['request_id'] = request_id
    
    # Add session ID if available
    session_id = getattr(logger, '_session_id', None)
    if session_id:
        event_dict['session_id'] = session_id
    
    # Add user ID if available
    user_id = getattr(logger, '_user_id', None)
    if user_id:
        event_dict['user_id'] = user_id
    
    return event_dict

def add_performance_context(logger, method_name, event_dict):
    """Add performance monitoring context"""
    # Add performance metrics if available
    duration = getattr(logger, '_duration', None)
    if duration is not None:
        event_dict['duration_ms'] = round(duration * 1000, 2)
    
    # Add operation type for performance tracking
    operation = getattr(logger, '_operation', None)
    if operation:
        event_dict['operation'] = operation
    
    return event_dict

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    if name is None:
        name = 'sol_glasses'
    
    return structlog.get_logger(name)

def get_audit_logger() -> structlog.BoundLogger:
    """Get audit logger for R12 compliance"""
    return structlog.get_logger('sol_glasses.audit')

def get_performance_logger() -> structlog.BoundLogger:
    """Get performance monitoring logger"""
    return structlog.get_logger('sol_glasses.performance')

class RequestContextLogger:
    """Context manager for request-scoped logging"""
    
    def __init__(self, logger: structlog.BoundLogger, **context):
        self.logger = logger
        self.context = context
        self.bound_logger = None
    
    def __enter__(self) -> structlog.BoundLogger:
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.bound_logger.error(
                "Request completed with error",
                exc_type=exc_type.__name__,
                exc_message=str(exc_val)
            )
        else:
            self.bound_logger.info("Request completed successfully")

class PerformanceTimer:
    """Context manager for performance timing"""
    
    def __init__(self, logger: structlog.BoundLogger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.debug("Operation started", operation=self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                "Operation failed",
                operation=self.operation,
                duration_ms=round(duration * 1000, 2),
                exc_type=exc_type.__name__,
                exc_message=str(exc_val)
            )
        else:
            self.logger.info(
                "Operation completed",
                operation=self.operation,
                duration_ms=round(duration * 1000, 2)
            )

# Audit logging functions for R12 compliance
def log_user_action(user_id: str, action: str, resource: str, **kwargs):
    """Log user action for audit trail"""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "User action",
        user_id=user_id,
        action=action,
        resource=resource,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )

def log_data_access(user_id: str, data_type: str, operation: str, **kwargs):
    """Log data access for privacy compliance"""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "Data access",
        user_id=user_id,
        data_type=data_type,
        operation=operation,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )

def log_data_deletion(user_id: str, data_types: list, **kwargs):
    """Log data deletion for GDPR compliance"""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "Data deletion",
        user_id=user_id,
        data_types=data_types,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )

# Performance monitoring functions
def log_gaze_processing_metrics(session_id: str, samples_processed: int, duration_ms: float, **kwargs):
    """Log gaze processing performance metrics"""
    perf_logger = get_performance_logger()
    perf_logger.info(
        "Gaze processing metrics",
        session_id=session_id,
        samples_processed=samples_processed,
        duration_ms=duration_ms,
        samples_per_second=round(samples_processed / (duration_ms / 1000), 2),
        **kwargs
    )

def log_database_operation_metrics(operation: str, duration_ms: float, **kwargs):
    """Log database operation performance metrics"""
    perf_logger = get_performance_logger()
    perf_logger.info(
        "Database operation metrics",
        operation=operation,
        duration_ms=duration_ms,
        **kwargs
    )

def log_websocket_metrics(session_id: str, message_count: int, duration_ms: float, **kwargs):
    """Log WebSocket performance metrics"""
    perf_logger = get_performance_logger()
    perf_logger.info(
        "WebSocket metrics",
        session_id=session_id,
        message_count=message_count,
        duration_ms=duration_ms,
        messages_per_second=round(message_count / (duration_ms / 1000), 2),
        **kwargs
    )

# Initialize logging if this module is imported
if not logging.getLogger().handlers:
    setup_logging()