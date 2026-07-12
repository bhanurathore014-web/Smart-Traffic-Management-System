"""
Logging Configuration
======================
Centralized Loguru logger setup for the entire application.

Features:
- Structured log format with timestamp, level, module, function
- File rotation (daily) with retention policy
- Separate error log file
- Rich console output (colored)
- JSON format option for production log aggregation

Usage:
    from config.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("System started")
    logger.error("Something went wrong", exc_info=True)
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from config.settings import get_settings


def setup_logging() -> None:
    """
    Configure Loguru logger with console and file handlers.

    This function should be called once at application startup,
    typically in main.py or the FastAPI lifespan handler.
    """
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default Loguru handler
    logger.remove()

    # ── Console handler ─────────────────────────────────────────
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    # ── Main rotating file handler ───────────────────────────────
    logger.add(
        log_dir / settings.log_file,
        level=settings.log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="gz",
        enqueue=True,          # Thread-safe async logging
        backtrace=True,
        diagnose=settings.debug,
    )

    # ── Error-only file handler ──────────────────────────────────
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}\n{exception}"
        ),
        rotation="1 week",
        retention="90 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info(
        f"Logging initialized | level={settings.log_level} | "
        f"file={log_dir / settings.log_file}"
    )


def get_logger(name: str):
    """
    Return a named logger bound to a specific module.

    Args:
        name: Module name (use __name__ for automatic naming).

    Returns:
        Loguru logger with module binding.

    Example:
        logger = get_logger(__name__)
        logger.info("Vehicle detected", extra={"lane": 1})
    """
    return logger.bind(module=name)
