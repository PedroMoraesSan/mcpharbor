import logging
import re

import structlog

SENSITIVE_PATTERN = re.compile(
    r"(token|secret|password|api_key|apikey|credential|pat|authorization)",
    re.IGNORECASE,
)


def _sanitize_processor(
    _logger: logging.Logger,
    _method_name: str,
    event_dict: dict,
) -> dict:
    for key in list(event_dict.keys()):
        if SENSITIVE_PATTERN.search(str(key)):
            event_dict[key] = "***REDACTED***"
    return event_dict


def configure_logging(level: str = "info") -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _sanitize_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
