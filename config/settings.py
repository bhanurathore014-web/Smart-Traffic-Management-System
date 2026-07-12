"""
Configuration Management
=========================
Centralized settings loaded from environment variables and .env file.
Uses Pydantic v2 BaseSettings for type-safe, validated configuration.

All settings can be overridden via environment variables or the .env file.
Never hardcode secrets — always use this module.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent


class AppSettings(BaseSettings):
    """Core application settings."""

    app_name: str = Field(default="Smart Traffic Management System")
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "production", "testing"] = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="dev-secret-change-in-production")

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./database/smart_traffic_dev.db"
    )
    alembic_database_url: str = Field(
        default="sqlite:///./database/smart_traffic_dev.db"
    )
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_echo: bool = Field(default=False)  # Set True to log all SQL

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class APISettings(BaseSettings):
    """FastAPI server configuration."""

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)
    api_workers: int = Field(default=1)
    cors_origins: list[str] = Field(default=["http://localhost:8501", "http://127.0.0.1:8501"])

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class DetectorSettings(BaseSettings):
    """YOLOv8 detection configuration."""

    yolo_model_size: Literal["n", "s", "m", "l", "x"] = Field(default="s")
    yolo_model_path: str = Field(default="models/weights/yolov8s.pt")
    yolo_conf_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    yolo_iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    yolo_device: str = Field(default="auto")  # auto | cpu | cuda | mps

    # Vehicle classes to detect (COCO class IDs)
    vehicle_classes: list[int] = Field(default=[1, 2, 3, 5, 7])
    # 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck

    # Class name mapping
    class_names: dict[int, str] = Field(
        default={
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }
    )

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class TrackerSettings(BaseSettings):
    """ByteTrack configuration."""

    tracker_track_thresh: float = Field(default=0.5, ge=0.0, le=1.0)
    tracker_track_buffer: int = Field(default=30)  # frames to keep lost tracks
    tracker_match_thresh: float = Field(default=0.8, ge=0.0, le=1.0)
    tracker_frame_rate: int = Field(default=25)

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class SignalSettings(BaseSettings):
    """Traffic signal timing configuration."""

    signal_min_green: int = Field(default=10, ge=5, le=30)   # seconds
    signal_max_green: int = Field(default=90, ge=30, le=180)  # seconds
    signal_yellow_time: int = Field(default=3, ge=2, le=10)   # seconds
    signal_total_cycle: int = Field(default=150, ge=60, le=300)  # seconds
    signal_num_lanes: int = Field(default=4, ge=1, le=8)

    @field_validator("signal_max_green")
    @classmethod
    def max_must_exceed_min(cls, v: int, info) -> int:
        """Ensure max green time is greater than min green time."""
        if "signal_min_green" in info.data and v <= info.data["signal_min_green"]:
            raise ValueError("signal_max_green must be greater than signal_min_green")
        return v

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class EmergencySettings(BaseSettings):
    """Emergency vehicle detection settings."""

    emergency_conf_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    emergency_confirm_frames: int = Field(default=3, ge=1, le=10)
    emergency_classes: list[str] = Field(
        default=["ambulance", "fire truck", "police car"]
    )
    emergency_absence_timeout: int = Field(default=30)  # frames before auto-resume

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class ANPRSettings(BaseSettings):
    """ANPR pipeline configuration."""

    anpr_min_confidence: float = Field(default=0.50, ge=0.0, le=1.0)
    anpr_ocr_primary: Literal["easyocr", "paddleocr"] = Field(default="easyocr")
    anpr_languages: list[str] = Field(default=["en"])
    anpr_save_images: bool = Field(default=True)
    anpr_image_dir: str = Field(default="outputs/plates")

    # Indian number plate regex pattern
    anpr_plate_pattern: str = Field(
        default=r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
    )

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class DensitySettings(BaseSettings):
    """Traffic density estimation settings."""

    density_weight_count: float = Field(default=0.5, ge=0.0, le=1.0)
    density_weight_occupancy: float = Field(default=0.3, ge=0.0, le=1.0)
    density_weight_speed: float = Field(default=0.2, ge=0.0, le=1.0)
    density_smooth_window: int = Field(default=5)  # seconds

    # Thresholds for classification
    density_low_threshold: float = Field(default=0.25)
    density_medium_threshold: float = Field(default=0.50)
    density_high_threshold: float = Field(default=0.75)

    # Max vehicles per lane (used for normalization)
    lane_max_capacity: int = Field(default=20)

    # Average speed when no speed data available (km/h)
    default_speed_kmh: float = Field(default=40.0)

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class VideoSettings(BaseSettings):
    """Video processing configuration."""

    video_source: str = Field(default="videos/sample_traffic.mp4")
    video_resize_width: int = Field(default=1280)
    video_resize_height: int = Field(default=720)
    video_frame_skip: int = Field(default=0, ge=0)
    video_output_dir: str = Field(default="outputs/frames")
    video_save_output: bool = Field(default=False)

    # Counting line Y position (fraction of frame height)
    counting_line_y: float = Field(default=0.6, ge=0.0, le=1.0)

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_dir: str = Field(default="logs")
    log_file: str = Field(default="smart_traffic.log")
    log_rotation: str = Field(default="1 day")
    log_retention: str = Field(default="30 days")

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class Settings(
    AppSettings,
    DatabaseSettings,
    APISettings,
    DetectorSettings,
    TrackerSettings,
    SignalSettings,
    EmergencySettings,
    ANPRSettings,
    DensitySettings,
    VideoSettings,
    LoggingSettings,
):
    """
    Master settings class combining all configuration groups.

    Usage:
        from config.settings import get_settings
        settings = get_settings()
        print(settings.api_port)
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached Settings instance.

    Using lru_cache ensures settings are loaded once and reused,
    avoiding repeated disk reads on every import.

    Returns:
        Settings: Validated, cached application settings.
    """
    return Settings()


# Convenience alias for direct import
settings = get_settings()
