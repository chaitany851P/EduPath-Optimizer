"""
Configuration management for EduPath Optimizer - Production Ready
Supports environment-based configuration for multiple deployment scenarios
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Environment(BaseSettings):
    """Main configuration class - supports all deployment environments"""

    # ─────────────────────────────────────────────────────────────
    # APPLICATION SETTINGS
    # ─────────────────────────────────────────────────────────────
    APP_NAME: str = Field(default="EduPath Optimizer", description="Application name")
    APP_VERSION: str = Field(default="2.0.0", description="Application version")
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ─────────────────────────────────────────────────────────────
    # SERVER SETTINGS
    # ─────────────────────────────────────────────────────────────
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=4, description="Number of Uvicorn workers")
    RELOAD: bool = Field(default=False, description="Auto-reload on code changes")
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # ─────────────────────────────────────────────────────────────
    # DATABASE SETTINGS
    # ─────────────────────────────────────────────────────────────
    MONGO_URI: Optional[str] = Field(default=None, description="Legacy MongoDB URI")
    DB_NAME: Optional[str] = Field(default=None, description="Legacy DB Name")
    MONGODB_URI: str = Field(
        default="mongodb+srv://user:password@cluster.mongodb.net",
        description="MongoDB connection URI"
    )
    MONGODB_DATABASE: str = Field(
        default="edupath_optimizer",
        description="MongoDB database name"
    )
    MONGODB_TIMEOUT: int = Field(
        default=30000,
        description="MongoDB connection timeout (ms)"
    )

    # ─────────────────────────────────────────────────────────────
    # SECURITY SETTINGS
    # ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="JWT secret key - MUST be changed in production"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration time (minutes)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time (days)"
    )

    # ─────────────────────────────────────────────────────────────
    # UNIVERSITY SETTINGS (Multi-Campus Support)
    # ─────────────────────────────────────────────────────────────
    UNIVERSITY_NAME: str = Field(
        default="Sample University",
        description="University name"
    )
    UNIVERSITY_ID: str = Field(
        default="UNIV_001",
        description="Unique university identifier"
    )
    ENABLE_MULTI_CAMPUS: bool = Field(
        default=True,
        description="Enable multi-campus support"
    )
    DEFAULT_CAMPUS_ID: str = Field(
        default="CAMPUS_001",
        description="Default campus ID"
    )
    ENABLE_MULTI_DEPARTMENT: bool = Field(
        default=True,
        description="Enable data segregation per department"
    )

    # ─────────────────────────────────────────────────────────────
    # FEATURE FLAGS
    # ─────────────────────────────────────────────────────────────
    ENABLE_PHASE_1: bool = Field(default=True, description="Attendance Optimization")
    ENABLE_PHASE_2: bool = Field(default=True, description="Exam Strategy")
    ENABLE_PHASE_3: bool = Field(default=True, description="Academic Bridge")
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(
        default=False,
        description="Send email notifications"
    )
    ENABLE_SMS_NOTIFICATIONS: bool = Field(
        default=False,
        description="Send SMS notifications"
    )

    # ─────────────────────────────────────────────────────────────
    # EMAIL CONFIGURATION
    # ─────────────────────────────────────────────────────────────
    EMAIL_ENABLED: bool = Field(default=False, description="Enable email service")
    SMTP_SERVER: str = Field(default="smtp.gmail.com", description="SMTP server")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SENDER_EMAIL: str = Field(
        default="noreply@university.edu",
        description="Sender email address"
    )

    # ─────────────────────────────────────────────────────────────
    # LDAP/AUTHENTICATION CONFIGURATION
    # ─────────────────────────────────────────────────────────────
    ENABLE_LDAP: bool = Field(
        default=False,
        description="Enable LDAP/Active Directory authentication"
    )
    LDAP_SERVER: str = Field(default="ldap.university.edu", description="LDAP server URL")
    LDAP_PORT: int = Field(default=389, description="LDAP port")
    LDAP_BASE_DN: str = Field(default="dc=university,dc=edu", description="LDAP base DN")
    LDAP_BIND_DN: str = Field(default="", description="LDAP bind DN")
    LDAP_BIND_PASSWORD: str = Field(default="", description="LDAP bind password")

    # ─────────────────────────────────────────────────────────────
    # BACKUP & RECOVERY
    # ─────────────────────────────────────────────────────────────
    ENABLE_BACKUPS: bool = Field(default=True, description="Enable database backups")
    BACKUP_FREQUENCY: str = Field(
        default="daily",
        description="Backup frequency: hourly, daily, weekly"
    )
    BACKUP_RETENTION_DAYS: int = Field(
        default=30,
        description="Backup retention period (days)"
    )
    BACKUP_LOCATION: str = Field(
        default="/backups",
        description="Backup storage location"
    )

    # ─────────────────────────────────────────────────────────────
    # MONITORING & LOGGING
    # ─────────────────────────────────────────────────────────────
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_SENTRY: bool = Field(default=False, description="Enable Sentry error tracking")
    SENTRY_DSN: str = Field(default="", description="Sentry DSN for error tracking")
    SENTRY_ENVIRONMENT: str = Field(default="production", description="Sentry environment")

    # ─────────────────────────────────────────────────────────────
    # VALIDATORS
    # ─────────────────────────────────────────────────────────────
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "CHANGE_ME_IN_PRODUCTION":
            import warnings
            warnings.warn(
                "SECRET_KEY is using default value! Change it in production!",
                UserWarning
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Load configuration
settings = Environment()


# ─────────────────────────────────────────────────────────────
# ENVIRONMENT-SPECIFIC SETTINGS
# ─────────────────────────────────────────────────────────────
def get_settings() -> Environment:
    """Get current settings instance"""
    return settings


def is_production() -> bool:
    """Check if running in production"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.ENVIRONMENT == "development"


def is_staging() -> bool:
    """Check if running in staging"""
    return settings.ENVIRONMENT == "staging"


# ─────────────────────────────────────────────────────────────
# CONFIGURATION DISPLAY (for debugging)
# ─────────────────────────────────────────────────────────────
def print_config_summary():
    """Print configuration summary (safe, no sensitive data)"""
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║          EduPath Optimizer Configuration                  ║
    ╚═══════════════════════════════════════════════════════════╝
    
    APP: {settings.APP_NAME} v{settings.APP_VERSION}
    ENVIRONMENT: {settings.ENVIRONMENT}
    DEBUG: {settings.DEBUG}
    
    SERVER:
      - Host: {settings.HOST}:{settings.PORT}
      - Workers: {settings.WORKERS}
      - Auto-reload: {settings.RELOAD}
    
    DATABASE:
      - Name: {settings.MONGODB_DATABASE}
      - Timeout: {settings.MONGODB_TIMEOUT}ms
    
    UNIVERSITY:
      - Name: {settings.UNIVERSITY_NAME}
      - Multi-Campus: {settings.ENABLE_MULTI_CAMPUS}
      - Multi-Department: {settings.ENABLE_MULTI_DEPARTMENT}
    
    FEATURES:
      - Phase 1 (Attendance): {settings.ENABLE_PHASE_1}
      - Phase 2 (Exam): {settings.ENABLE_PHASE_2}
      - Phase 3 (Bridge): {settings.ENABLE_PHASE_3}
      - Email: {settings.ENABLE_EMAIL_NOTIFICATIONS}
    
    SECURITY:
      - JWT Algorithm: {settings.ALGORITHM}
      - Token Expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}min
    
    ╚═══════════════════════════════════════════════════════════╝
    """)
