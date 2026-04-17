"""
DeepTrace — Brute Force / Credential Attack Rule (multi-signal)

Fires only when:
  1. login_count ≥ threshold
  2. login_count / flow_count ≥ BRUTEFORCE_FRAC  (default 0.20)
  3. packet_count ≥ BRUTEFORCE_MIN_PACKETS
"""
from __future__ import annotations

from analytics.ip_profile import IPProfile
from app.config import BRUTEFORCE_FRAC, BRUTEFORCE_MIN_PACKETS, DEBUG_DETECTION
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds
from app.logging_config import log


def evaluate(
    ip:      str,
    profile: IPProfile,
    thresh:  Thresholds,
    alerts:  AlertManager,
) -> None:
    if profile.flow_count == 0:
        return

    frac = profile.login_count / profile.flow_count

    if DEBUG_DETECTION:
        log.debug(
            "[BruteForce] eval",
            extra={
                "ip": ip,
                "login_count": profile.login_count,
                "threshold": thresh.login,
                "frac": round(frac, 3),
                "min_frac": BRUTEFORCE_FRAC,
                "packets": profile.packet_count,
                "min_packets": BRUTEFORCE_MIN_PACKETS,
            },
        )

    if (
        profile.login_count     >= thresh.login
        and frac                >= BRUTEFORCE_FRAC
        and profile.packet_count >= BRUTEFORCE_MIN_PACKETS
    ):
        alerts.flag(
            "Possible Brute Force",
            alerts.confidence(profile.login_count, thresh.login),
            f"{ip} made {profile.login_count} login-port connections "
            f"({frac * 100:.1f}% of {profile.flow_count} flows, "
            f"{profile.packet_count} total packets).",
            ip,
            f"[thresh:{thresh.login:.1f}]",
        )
