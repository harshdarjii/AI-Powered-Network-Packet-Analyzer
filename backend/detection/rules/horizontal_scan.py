"""
DeepTrace — Horizontal Scan Rule (multi-signal)

Fires only when:
  1. unique destination IPs ≥ threshold
  2. packet_count ≥ HORIZ_MIN_PACKETS
"""
from __future__ import annotations

from analytics.ip_profile import IPProfile
from app.config import HORIZ_MIN_PACKETS, DEBUG_DETECTION
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds
from app.logging_config import log


def evaluate(
    ip:      str,
    profile: IPProfile,
    thresh:  Thresholds,
    alerts:  AlertManager,
) -> None:
    val = len(profile.dst_ips)

    if DEBUG_DETECTION:
        log.debug(
            "[HorizScan] eval",
            extra={
                "ip": ip,
                "unique_hosts": val,
                "threshold": thresh.ips,
                "packets": profile.packet_count,
                "min_packets": HORIZ_MIN_PACKETS,
            },
        )

    if val >= thresh.ips and profile.packet_count >= HORIZ_MIN_PACKETS:
        alerts.flag(
            "Horizontal Scan",
            alerts.confidence(val, thresh.ips),
            f"{ip} contacted {val} unique hosts "
            f"({profile.packet_count} packets).",
            ip,
            f"[thresh:{thresh.ips:.1f}]",
        )
