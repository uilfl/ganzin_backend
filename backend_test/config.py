#!/usr/bin/env python3
"""
Enhanced Configuration Management for Sol Glasses Backend
Production-ready configuration with validation and type safety
"""

import os
import logging
from typing import Optional, List, Any
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

# Setup basic logging for config loading
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration with validation"""
    url: str = "postgresql://localhost:5432/sol_glasses"
    min_pool_size: int = 2
    max_pool_size: int = 20
    command_timeout: int = 60
    ssl_mode: str = "prefer"
    
    def __post_init__(self):
        """Validate database configuration"""
        try:
            parsed = urlparse(self.url)
            if not parsed.scheme.startswith('postgres'):
                raise ValueError(f"Invalid database URL scheme: {parsed.scheme}")
            if not parsed.hostname:
                raise ValueError("Database hostname is required")
        except Exception as e:
            logger.error(f"Invalid database configuration: {e}")
            raise
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            url=os.getenv('DATABASE_URL', cls.url),
            min_pool_size=int(os.getenv('DB_MIN_POOL_SIZE', cls.min_pool_size)),
            max_pool_size=int(os.getenv('DB_MAX_POOL_SIZE', cls.max_pool_size)),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', cls.command_timeout)),
            ssl_mode=os.getenv('DB_SSL_MODE', cls.ssl_mode)
        )

@dataclass
class SolSDKConfig:
    """Sol SDK configuration with connection validation"""
    default_address: str = "192.168.1.117"
    default_port: int = 8080
    rtsp_port: int = 8086
    connection_timeout: float = 2.0
    read_timeout: float = 7.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate Sol SDK configuration"""
        if self.default_port < 1 or self.default_port > 65535:
            raise ValueError(f"Invalid port number: {self.default_port}")
        if self.connection_timeout <= 0:
            raise ValueError("Connection timeout must be positive")
    
    @classmethod
    def from_env(cls) -> 'SolSDKConfig':
        return cls(
            default_address=os.getenv('SOL_GLASSES_IP', cls.default_address),
            default_port=int(os.getenv('SOL_GLASSES_PORT', cls.default_port)),
            rtsp_port=int(os.getenv('SOL_RTSP_PORT', cls.rtsp_port)),
            connection_timeout=float(os.getenv('SOL_CONNECT_TIMEOUT', cls.connection_timeout)),
            read_timeout=float(os.getenv('SOL_READ_TIMEOUT', cls.read_timeout)),
            max_retries=int(os.getenv('SOL_MAX_RETRIES', cls.max_retries)),
            retry_delay=float(os.getenv('SOL_RETRY_DELAY', cls.retry_delay))
        )

@dataclass
class ProcessingConfig:
    """Gaze processing configuration with R4 requirements"""
    fixation_window_ms: int = 100
    fixation_dispersion_threshold: float = 1.0  # degrees visual angle
    confidence_threshold: float = 0.8  # R1 requirement: ≥0.8
    sampling_rate_hz: float = 120.0  # R1 requirement: ≥120 Hz
    buffer_size: int = 50
    event_detection_precision_target: float = 0.95  # R4: ≥95%
    
    # Screen/display parameters for coordinate conversion
    screen_width_px: int = 1920
    screen_height_px: int = 1080
    viewing_distance_cm: float = 60.0
    pixels_per_degree: float = 30.0  # Approximate conversion
    
    def __post_init__(self):
        """Validate processing configuration"""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        if self.sampling_rate_hz < 60.0:
            logger.warning(f"Sampling rate {self.sampling_rate_hz} Hz is below recommended 120Hz")
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        return cls(
            fixation_window_ms=int(os.getenv('FIXATION_WINDOW_MS', cls.fixation_window_ms)),
            fixation_dispersion_threshold=float(os.getenv('FIXATION_THRESHOLD', cls.fixation_dispersion_threshold)),
            confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', cls.confidence_threshold)),
            sampling_rate_hz=float(os.getenv('SAMPLING_RATE_HZ', cls.sampling_rate_hz)),
            buffer_size=int(os.getenv('PROCESSING_BUFFER_SIZE', cls.buffer_size)),
            event_detection_precision_target=float(os.getenv('EVENT_PRECISION_TARGET', cls.event_detection_precision_target)),
            screen_width_px=int(os.getenv('SCREEN_WIDTH_PX', cls.screen_width_px)),
            screen_height_px=int(os.getenv('SCREEN_HEIGHT_PX', cls.screen_height_px)),
            viewing_distance_cm=float(os.getenv('VIEWING_DISTANCE_CM', cls.viewing_distance_cm)),
            pixels_per_degree=float(os.getenv('PIXELS_PER_DEGREE', cls.pixels_per_degree))
        )

@dataclass
class AdaptationConfig:
    """Adaptation service configuration with R5/R7/R8 requirements"""
    # R7: Vocabulary assistance timing
    vocabulary_fixation_threshold_ms: int = 1500  # >1.5s fixation
    
    # R8: Grammar help timing  
    grammar_fixation_threshold_ms: int = 2000    # Complex sentence detection
    
    # R5: Performance requirements
    feedback_latency_target_ms: int = 200        # ≤200ms end-to-end
    feedback_rate_limit_ms: int = 5000           # Max 1 feedback per 5 seconds
    max_feedback_history: int = 10
    
    # Rule engine settings
    enable_vocabulary_rules: bool = True
    enable_grammar_rules: bool = True
    enable_general_hints: bool = True
    
    def __post_init__(self):
        """Validate adaptation configuration"""
        if self.feedback_latency_target_ms > 500:
            logger.warning(f"Feedback latency target {self.feedback_latency_target_ms}ms exceeds R5 requirement (≤200ms)")
    
    @classmethod
    def from_env(cls) -> 'AdaptationConfig':
        return cls(
            vocabulary_fixation_threshold_ms=int(os.getenv('VOCAB_THRESHOLD_MS', cls.vocabulary_fixation_threshold_ms)),
            grammar_fixation_threshold_ms=int(os.getenv('GRAMMAR_THRESHOLD_MS', cls.grammar_fixation_threshold_ms)),
            feedback_latency_target_ms=int(os.getenv('FEEDBACK_LATENCY_TARGET_MS', cls.feedback_latency_target_ms)),
            feedback_rate_limit_ms=int(os.getenv('FEEDBACK_RATE_LIMIT_MS', cls.feedback_rate_limit_ms)),
            max_feedback_history=int(os.getenv('MAX_FEEDBACK_HISTORY', cls.max_feedback_history)),
            enable_vocabulary_rules=os.getenv('ENABLE_VOCAB_RULES', 'true').lower() == 'true',
            enable_grammar_rules=os.getenv('ENABLE_GRAMMAR_RULES', 'true').lower() == 'true',
            enable_general_hints=os.getenv('ENABLE_GENERAL_HINTS', 'true').lower() == 'true'
        )

@dataclass
class ServerConfig:
    """Server configuration with security settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    log_level: str = "info"
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    
    # Security settings
    enable_cors: bool = True
    max_connections: int = 1000
    timeout_keep_alive: int = 30
    
    # Performance settings
    workers: int = 1
    max_requests: int = 10000
    max_requests_jitter: int = 1000
    
    def __post_init__(self):
        """Validate server configuration"""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        if self.log_level not in ['debug', 'info', 'warning', 'error']:
            raise ValueError(f"Invalid log level: {self.log_level}")
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        cors_origins_str = os.getenv('CORS_ORIGINS', '')
        cors_origins = [origin.strip() for origin in cors_origins_str.split(',')] if cors_origins_str else cls().cors_origins
        
        return cls(
            host=os.getenv('SERVER_HOST', cls.host),
            port=int(os.getenv('SERVER_PORT', cls.port)),
            reload=os.getenv('SERVER_RELOAD', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', cls.log_level),
            cors_origins=cors_origins,
            enable_cors=os.getenv('ENABLE_CORS', 'true').lower() == 'true',
            max_connections=int(os.getenv('MAX_CONNECTIONS', cls.max_connections)),
            timeout_keep_alive=int(os.getenv('TIMEOUT_KEEP_ALIVE', cls.timeout_keep_alive)),
            workers=int(os.getenv('WORKERS', cls.workers)),
            max_requests=int(os.getenv('MAX_REQUESTS', cls.max_requests)),
            max_requests_jitter=int(os.getenv('MAX_REQUESTS_JITTER', cls.max_requests_jitter))
        )

@dataclass
class SecurityConfig:
    """Security configuration for R12 compliance"""
    enable_encryption_at_rest: bool = True  # R12: AES-256
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    
    # GDPR compliance settings
    enable_data_deletion: bool = True
    deletion_sla_hours: int = 72  # R12: ≤72h deletion
    enable_audit_logging: bool = True
    
    def __post_init__(self):
        """Validate security configuration"""
        if len(self.jwt_secret_key) < 32:
            logger.warning("JWT secret key is too short, use at least 32 characters in production")
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        return cls(
            enable_encryption_at_rest=os.getenv('ENABLE_ENCRYPTION_AT_REST', 'true').lower() == 'true',
            jwt_secret_key=os.getenv('JWT_SECRET_KEY', cls.jwt_secret_key),
            jwt_algorithm=os.getenv('JWT_ALGORITHM', cls.jwt_algorithm),
            jwt_expire_minutes=int(os.getenv('JWT_EXPIRE_MINUTES', cls.jwt_expire_minutes)),
            enable_data_deletion=os.getenv('ENABLE_DATA_DELETION', 'true').lower() == 'true',
            deletion_sla_hours=int(os.getenv('DELETION_SLA_HOURS', cls.deletion_sla_hours)),
            enable_audit_logging=os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
        )

@dataclass
class AppConfig:
    """Complete application configuration"""
    database: DatabaseConfig
    sol_sdk: SolSDKConfig
    processing: ProcessingConfig
    adaptation: AdaptationConfig
    server: ServerConfig
    security: SecurityConfig
    
    # Feature flags
    use_database: bool = True
    use_processing: bool = True
    use_mock_sol_client: bool = False
    debug_mode: bool = False
    enable_metrics: bool = True
    
    # Environment info
    environment: str = "development"
    version: str = "1.0.0"
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Warn about production readiness
        if self.environment == "production" and self.debug_mode:
            logger.warning("Debug mode is enabled in production environment")
        
        if self.environment == "production" and self.use_mock_sol_client:
            logger.warning("Mock Sol client is enabled in production environment")
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        environment = os.getenv('ENVIRONMENT', 'development')
        
        config = cls(
            database=DatabaseConfig.from_env(),
            sol_sdk=SolSDKConfig.from_env(),
            processing=ProcessingConfig.from_env(),
            adaptation=AdaptationConfig.from_env(),
            server=ServerConfig.from_env(),
            security=SecurityConfig.from_env(),
            use_database=os.getenv('USE_DATABASE', 'true').lower() == 'true',
            use_processing=os.getenv('USE_PROCESSING', 'true').lower() == 'true',
            use_mock_sol_client=os.getenv('USE_MOCK_SOL_CLIENT', 'false').lower() == 'true',
            debug_mode=os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            enable_metrics=os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            environment=environment,
            version=os.getenv('APP_VERSION', cls.version)
        )
        
        logger.info(f"Configuration loaded for environment: {environment}")
        return config
    
    def validate(self) -> bool:
        """Comprehensive configuration validation"""
        try:
            # Validate all sub-configurations
            self.database.__post_init__()
            self.sol_sdk.__post_init__()
            self.processing.__post_init__()
            self.adaptation.__post_init__()
            self.server.__post_init__()
            self.security.__post_init__()
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

# Global configuration instance
config = AppConfig.from_env()

# Validation on import
if not config.validate():
    raise RuntimeError("Invalid configuration detected")

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config

def reload_config() -> AppConfig:
    """Reload configuration from environment"""
    global config
    config = AppConfig.from_env()
    if not config.validate():
        raise RuntimeError("Invalid configuration after reload")
    return config

# Environment detection helpers
def is_development() -> bool:
    return config.environment == 'development'

def is_production() -> bool:
    return config.environment == 'production'

def is_testing() -> bool:
    return config.environment == 'testing'