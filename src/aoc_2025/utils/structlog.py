"""
Structured logging configuration for Capy ETL.

Uses structlog for consistent, structured logging across the application.
"""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(level: int = logging.INFO) -> None:
  """
  Configure structured logging for the application.

  Args:
      level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
      log_to_file: Whether to also log to files in ./logs/ directory
  """
  # Configure standard library logging (console only)
  logging.basicConfig(
    format="%(message)s",
    level=level,
    handlers=[logging.StreamHandler(sys.stdout)],
  )

  structlog.configure(
    processors=[
      structlog.contextvars.merge_contextvars,
      structlog.processors.add_log_level,
      structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
      structlog.processors.ExceptionPrettyPrinter(),
      structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(level),
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
  )


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
  """
  Get a configured logger instance.

  Args:
      name: Logger name (usually __name__)

  Returns:
      Structlog BoundLogger instance
  """
  logger: structlog.typing.FilteringBoundLogger = structlog.get_logger(name)
  return logger


# Initialize logging on import
setup_logging(logging.INFO)
