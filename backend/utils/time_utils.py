"""
DeepTrace — Time Utility Functions
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional


def parse_timestamp(ts_raw: str) -> Optional[datetime]:
    """
    Parse a timestamp string.
    Tries ISO-8601 first, then float Unix epoch (Wireshark / tcpdump exports).
    Returns None on failure — callers must handle None safely.
    """
    if not ts_raw:
        return None
    try:
        return datetime.fromisoformat(str(ts_raw))
    except (ValueError, TypeError):
        pass
    try:
        return datetime.fromtimestamp(float(ts_raw))
    except (ValueError, TypeError, OSError, OverflowError):
        return None
