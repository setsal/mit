"""Logging configuration for the MIT framework."""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

# Track if logging has been set up
_logging_configured = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the MIT namespace.

    Args:
        name: Logger name (will be prefixed with 'mit.')

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"mit.{name}")


def setup_logging(level: LogLevel = "INFO") -> None:
    """Configure logging for the MIT framework.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    global _logging_configured

    if _logging_configured:
        return

    # Configure root MIT logger
    mit_logger = logging.getLogger("mit")
    mit_logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add handler to MIT logger
    mit_logger.addHandler(handler)

    # Prevent propagation to root logger
    mit_logger.propagate = False

    _logging_configured = True


# Convenience loggers for common components
router_logger = get_logger("router")
coordinator_logger = get_logger("coordinator")
agent_logger = get_logger("agent")
rag_logger = get_logger("rag")
