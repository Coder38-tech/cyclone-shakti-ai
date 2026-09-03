import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured logging for the application.

    Args:
        level: Logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Root logger configured for console + optional file output.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger("cyclone_shakti")
    root.setLevel(log_level)
    root.propagate = False

    if root.handlers:
        return root

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "cyclone_shakti.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError:
        pass

    return root


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a module-scoped logger under the application namespace."""
    base = logging.getLogger("cyclone_shakti")
    if not base.handlers:
        setup_logging()
    if name:
        return base.getChild(name)
    return base
