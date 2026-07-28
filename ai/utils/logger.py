"""
logger.py — Centralised Logging Configuration.

Provides a single `get_logger()` factory that returns a named Logger
pre-configured with:
    - A rotating file handler (saves to LOG_FILE_PATH)
    - A coloured console handler for readable terminal output

Import pattern:
    from utils.logger import get_logger
    log = get_logger(__name__)

Author: [Author Placeholder]
Version: 1.0.0
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import config


# ---------------------------------------------------------------------------
# ANSI Colour Codes for Console Output
# ---------------------------------------------------------------------------

class _ColourFormatter(logging.Formatter):
    """
    Custom log formatter that adds ANSI colour codes to console output.
    Colours are stripped automatically on non-TTY outputs (e.g. pipes, files).
    """

    LEVEL_COLOURS: dict[int, str] = {
        logging.DEBUG:    "\033[36m",    # Cyan
        logging.INFO:     "\033[32m",    # Green
        logging.WARNING:  "\033[33m",    # Yellow
        logging.ERROR:    "\033[31m",    # Red
        logging.CRITICAL: "\033[35;1m",  # Magenta bold
    }
    RESET: str = "\033[0m"

    _FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    _DATE_FMT: str = "%H:%M:%S"

    def __init__(self, use_colour: bool = True) -> None:
        super().__init__(fmt=self._FORMAT, datefmt=self._DATE_FMT)
        self._use_colour = use_colour

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        if self._use_colour:
            colour = self.LEVEL_COLOURS.get(record.levelno, "")
            formatted = f"{colour}{formatted}{self.RESET}"
        return formatted


# ---------------------------------------------------------------------------
# Module-level registry to avoid duplicate handlers on re-import
# ---------------------------------------------------------------------------

_configured_loggers: set[str] = set()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Return a named Logger with rotating file and coloured console handlers.

    Handlers are added only once per logger name — safe to call repeatedly
    from multiple modules with the same ``name``.

    Args:
        name:  Logger name, typically ``__name__`` of the calling module.
        level: Override log level string (e.g. "DEBUG"). Defaults to the
               value set in ``config.LOG_LEVEL``.

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)

    # Skip reconfiguration if this logger was already set up
    if name in _configured_loggers:
        return logger

    _configured_loggers.add(name)

    # Resolve log level
    resolved_level_str: str = (level or config.LOG_LEVEL).upper()
    resolved_level: int = getattr(logging, resolved_level_str, logging.INFO)
    logger.setLevel(resolved_level)

    # ------------------------------------------------------------------
    # Console handler — coloured output to stdout
    # ------------------------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(resolved_level)
    use_colour = sys.stdout.isatty()
    console_handler.setFormatter(_ColourFormatter(use_colour=use_colour))
    logger.addHandler(console_handler)

    # ------------------------------------------------------------------
    # Rotating file handler — persists logs to disk
    # ------------------------------------------------------------------
    _ensure_log_dir()
    file_handler = RotatingFileHandler(
        filename=config.LOG_FILE_PATH,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    # Prevent log records from propagating to the root logger
    logger.propagate = False

    return logger


def _ensure_log_dir() -> None:
    """
    Create the log directory if it does not already exist.
    """
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
