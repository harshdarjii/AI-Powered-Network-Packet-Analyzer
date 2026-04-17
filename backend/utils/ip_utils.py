"""
DeepTrace — IP Utility Functions
"""
from __future__ import annotations

import struct
import socket


def _ip_to_int(ip: str) -> int:
    try:
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    except (OSError, struct.error):
        return 0


# Pre-computed RFC-1918 + loopback + link-local ranges
_PRIVATE_RANGES = [
    (_ip_to_int("10.0.0.0"),      _ip_to_int("10.255.255.255")),
    (_ip_to_int("172.16.0.0"),    _ip_to_int("172.31.255.255")),
    (_ip_to_int("192.168.0.0"),   _ip_to_int("192.168.255.255")),
    (_ip_to_int("127.0.0.0"),     _ip_to_int("127.255.255.255")),
    (_ip_to_int("169.254.0.0"),   _ip_to_int("169.254.255.255")),
]


def is_private_ip(ip: str) -> bool:
    """Return True if the IPv4 address falls within a private / RFC-1918 range."""
    n = _ip_to_int(ip)
    if n == 0:
        return False
    return any(lo <= n <= hi for lo, hi in _PRIVATE_RANGES)
