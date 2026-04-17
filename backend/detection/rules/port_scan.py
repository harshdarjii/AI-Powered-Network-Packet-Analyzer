"""
DeepTrace — Vertical Port Scan Rule (multi-signal)

Fires only when:
  1. unique destination ports ≥ threshold
  2. packet_count ≥ PORTSCAN_MIN_PACKETS
  3. flow duration ≥ PORTSCAN_MIN_DURATION seconds
"""
from __future__ import annotations

from analytics.ip_profile import IPProfile
from app.config import PORTSCAN_MIN_PACKETS, PORTSCAN_MIN_DURATION, DEBUG_DETECTION
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds
from app.logging_config import log


def evaluate(
    ip:       str,
    profile:  IPProfile,
    thresh:   Thresholds,
    alerts:   AlertManager,
) -> None:
    val      = len(profile.dst_ports)
    duration = profile.duration_secs

    if DEBUG_DETECTION:
        log.debug(
            "[PortScan] eval",
            extra={
                "ip": ip,
                "unique_ports": val,
                "threshold": thresh.ports,
                "packets": profile.packet_count,
                "min_packets": PORTSCAN_MIN_PACKETS,
                "duration": round(duration, 2),
                "min_duration": PORTSCAN_MIN_DURATION,
            },
        )

    if (
        val                   >= thresh.ports
        and profile.packet_count >= PORTSCAN_MIN_PACKETS
        and duration             >= PORTSCAN_MIN_DURATION
    ):
        alerts.flag(
            "Vertical Port Scan",
            alerts.confidence(val, thresh.ports),
            f"{ip} contacted {val} unique destination ports "
            f"({profile.packet_count} packets over {duration:.1f}s).",
            ip,
            f"[thresh:{thresh.ports:.1f}]",
        )
