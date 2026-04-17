"""
DeepTrace — DNS Tunneling Rule (multi-signal)

Fires only when:
  1. dns_count ≥ threshold
  2. dns_count / flow_count ≥ DNS_FRAC_THRESHOLD  (default 0.40)
  3. flow_count ≥ DNS_MIN_FLOWS

Normal browser DNS usage is typically well below 40% of total flows.
"""
from __future__ import annotations

from analytics.ip_profile import IPProfile
from app.config import DNS_FRAC_THRESHOLD, DNS_MIN_FLOWS, DEBUG_DETECTION
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds
from app.logging_config import log


def evaluate(
    ip:      str,
    profile: IPProfile,
    thresh:  Thresholds,
    alerts:  AlertManager,
) -> None:
    if profile.flow_count < DNS_MIN_FLOWS:
        return

    frac = profile.dns_count / profile.flow_count

    if DEBUG_DETECTION:
        log.debug(
            "[DNS] eval",
            extra={
                "ip": ip,
                "dns_count": profile.dns_count,
                "threshold": thresh.dns,
                "frac": round(frac, 3),
                "min_frac": DNS_FRAC_THRESHOLD,
                "flows": profile.flow_count,
                "min_flows": DNS_MIN_FLOWS,
            },
        )

    if profile.dns_count >= thresh.dns and frac >= DNS_FRAC_THRESHOLD:
        alerts.flag(
            "Possible DNS Tunneling",
            alerts.confidence(profile.dns_count, thresh.dns),
            f"{ip} made {profile.dns_count} DNS queries "
            f"({frac * 100:.1f}% of {profile.flow_count} flows).",
            ip,
            f"[thresh:{thresh.dns:.1f}]",
        )
