"""
DeepTrace — Upload Validation & Security Helpers
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from fastapi import HTTPException

# Magic bytes → expected extension
_MAGIC_SIGNATURES: List[Tuple[bytes, str]] = [
    (b"\xd4\xc3\xb2\xa1", ".pcap"),
    (b"\xa1\xb2\xc3\xd4", ".pcap"),
    (b"\x0a\x0d\x0d\x0a", ".pcapng"),
]


def validate_mime(first_bytes: bytes, declared_ext: str) -> None:
    """Raise HTTP 415 if magic bytes do not match the declared extension."""
    for magic, ext in _MAGIC_SIGNATURES:
        if first_bytes[:4] == magic[:4]:
            if declared_ext != ext:
                raise HTTPException(
                    status_code=415,
                    detail=(
                        f"File content looks like {ext} "
                        f"but filename declares {declared_ext}."
                    ),
                )
            return
    if declared_ext in (".pcap", ".pcapng"):
        raise HTTPException(
            status_code=415,
            detail="File does not have valid PCAP magic bytes.",
        )


def safe_filename(filename: str) -> str:
    """Strip path components and whitelist safe characters."""
    name = Path(filename).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name or "upload"


def sanitise_csv_field(value: str) -> str:
    """Prefix formula-injection characters so spreadsheets won't execute them."""
    if value and value[0] in ("=", "+", "-", "@"):
        return "\t" + value
    return value
