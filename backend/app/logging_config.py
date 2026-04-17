"""
DeepTrace — Structured JSON Logging
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record — friendly to log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        doc: Dict[str, Any] = {
            "ts":     datetime.now(timezone.utc).isoformat(),
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.getMessage(),
        }
        if record.exc_info:
            doc["exc"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k not in logging.LogRecord.__dict__ and k not in ("message", "asctime"):
                doc[k] = v
        return json.dumps(doc)


def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(_JsonFormatter())
        logger.addHandler(h)
    logger.setLevel(os.environ.get("DEEPTRACE_LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger


log = build_logger("deeptrace")
