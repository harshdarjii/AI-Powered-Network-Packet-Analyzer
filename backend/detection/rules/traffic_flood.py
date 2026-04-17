"""
DeepTrace — Traffic Flooding & Related Rules

Covers:
  • Traffic Flooding (suppressed on short captures)
  • Data Exfiltration Suspicion
  • ICMP Sweep
  • Heavy-Hitter (via CMS)
  • Oversized Single Flow (requires repetition)
"""
from __future__ import annotations

from analytics.ip_profile import IPProfile
from analytics.sketches.countmin_sketch import CountMinSketch
from app.config import (
    DEBUG_DETECTION, LARGE_FLOW_MIN_REPEAT,
)
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds
from app.logging_config import log


def evaluate_flood(
    ip:            str,
    profile:       IPProfile,
    thresh:        Thresholds,
    alerts:        AlertManager,
    short_capture: bool,
    total_bytes:   int,
) -> None:
    """Traffic Flooding + Data Exfiltration + ICMP Sweep."""

    # ── 1. Traffic Flooding (rate-based — suppressed on short captures) ───────
    if not short_capture and profile.packet_count >= thresh.packets:
        if DEBUG_DETECTION:
            log.debug(
                "[Flood] triggered",
                extra={"ip": ip, "packets": profile.packet_count, "thresh": thresh.packets},
            )
        alerts.flag(
            "Traffic Flooding",
            alerts.confidence(profile.packet_count, thresh.packets),
            f"{ip} sent {profile.packet_count} packets at {profile.pps:.1f} pps.",
            ip,
            f"[thresh:{thresh.packets:.1f}]",
        )

    # ── 2. Data Exfiltration ──────────────────────────────────────────────────
    if profile.byte_count >= thresh.bytes_:
        pct = (profile.byte_count / total_bytes * 100) if total_bytes > 0 else 0.0
        if DEBUG_DETECTION:
            log.debug(
                "[Exfil] triggered",
                extra={"ip": ip, "bytes": profile.byte_count, "thresh": thresh.bytes_},
            )
        alerts.flag(
            "Data Exfiltration Suspicion",
            alerts.confidence(profile.byte_count, thresh.bytes_),
            f"{ip} transferred {profile.byte_count / 1_048_576:.2f} MB "
            f"({pct:.1f}% of capture).",
            ip,
            f"[thresh:{thresh.bytes_ / 1_048_576:.2f} MB]",
        )

    # ── 3. ICMP Sweep ─────────────────────────────────────────────────────────
    val = len(profile.icmp_dst_ips)
    if val >= thresh.icmp:
        if DEBUG_DETECTION:
            log.debug(
                "[ICMP] triggered",
                extra={"ip": ip, "icmp_hosts": val, "thresh": thresh.icmp},
            )
        alerts.flag(
            "ICMP Sweep",
            alerts.confidence(val, thresh.icmp),
            f"{ip} sent ICMP to {val} unique hosts.",
            ip,
            f"[thresh:{thresh.icmp:.1f}]",
        )


def evaluate_large_flow(
    ip:      str,
    profile: IPProfile,
    thresh:  Thresholds,
    alerts:  AlertManager,
) -> None:
    """
    Oversized flow detection — requires LARGE_FLOW_MIN_REPEAT repetitions.
    A single large download should NOT trigger an alert.
    """
    if profile.large_flow_count >= LARGE_FLOW_MIN_REPEAT:
        if DEBUG_DETECTION:
            log.debug(
                "[LargeFlow] triggered",
                extra={
                    "ip": ip,
                    "repeat": profile.large_flow_count,
                    "min_repeat": LARGE_FLOW_MIN_REPEAT,
                },
            )
        alerts.flag(
            "Repeated Oversized Flows",
            alerts.confidence(profile.large_flow_count, LARGE_FLOW_MIN_REPEAT),
            f"{ip} sent {profile.large_flow_count} oversized flows "
            f"(each ≥ {thresh.flowsize / 1_048_576:.2f} MB).",
            ip,
            f"[repeat:{profile.large_flow_count}]",
        )


def evaluate_heavy_hitter(
    ip:           str,
    profile:      IPProfile,
    cms:          CountMinSketch,
    thresh:       Thresholds,
    alerts:       AlertManager,
    total_flows:  int,
    total_unique: int,
) -> None:
    """Heavy-Hitter via Count-Min Sketch — catches spoofed-IP floods."""
    cms_threshold = max((total_flows / max(total_unique, 1)) * 10, thresh.packets)
    cms_est       = cms.estimate(ip)

    if DEBUG_DETECTION:
        log.debug(
            "[CMS] eval",
            extra={"ip": ip, "cms_est": cms_est, "cms_thresh": cms_threshold},
        )

    if cms_est >= cms_threshold:
        alerts.flag(
            "Heavy-Hitter Traffic",
            alerts.confidence(cms_est, cms_threshold),
            f"{ip} is a heavy hitter (~{cms_est} packets estimated by CMS).",
            ip,
            f"[cms_thresh:{cms_threshold:.0f}]",
        )
