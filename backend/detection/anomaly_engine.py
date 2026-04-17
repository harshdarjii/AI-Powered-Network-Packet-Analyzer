"""
DeepTrace v7.1 — Anomaly Detection Engine

Single-pass disk-streaming detection pipeline.

Key improvements over v6.1:
  • Adaptive thresholds — floor values used until 50+ sketch samples collected,
    then real statistics kick in automatically (replaces old warmup phase)
  • Detection fires from the very first flow — no dead zone
  • Minimum evidence filter (ignore IPs with too few packets/flows)
  • Multi-signal rules (all rules require ≥2 corroborating signals)
  • Internal-IP aware thresholds (RFC-1918 hosts get higher thresholds)
  • Profile TTL / sliding window (stale profiles discarded)
  • Alert cooldown (one anomaly per IP per rule per 60 s)
  • Oversized flow repetition guard (single large download ≠ alert)
  • Higher threshold floors (conservative defaults)
"""
from __future__ import annotations

import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from analytics.ip_profile import IPProfile
from analytics.sampling.reservoir_sampler import ReservoirSampler
from analytics.sketches.countmin_sketch import CountMinSketch
from analytics.sketches.fixed_sketch import FixedSketch
from app.config import (
    MAX_TRACKED_IPS, MIN_DURATION_SECS, SKETCH_SIZE,
    MIN_PACKETS_FOR_DETECTION, MIN_FLOWS_FOR_DETECTION,
    PROFILE_TTL_SECS, DEBUG_DETECTION,
)
from app.logging_config import log
from detection.alert_manager import AlertManager
from detection.thresholds import Thresholds, compute_thresholds
from detection.rules import port_scan, horizontal_scan, dns_tunnel, brute_force, traffic_flood
from ingestion.file_streamer import get_disk_stream
from utils.ip_utils import is_private_ip


def run_detection_from_disk(filepath: Path) -> dict:
    """
    Full streaming detection pipeline.

    RAM budget (default config, worst case):
    ┌──────────────────────────────────────────┬──────────────┐
    │ Component                                │ RAM          │
    ├──────────────────────────────────────────┼──────────────┤
    │ Buffered file read (256 KB)              │ 256 KB       │
    │ Current flow dict                        │ ~1 KB        │
    │ IPProfile × MAX_TRACKED_IPS (500 K cap)  │ ≤ 200 MB     │
    │ CountMinSketch (4 × 2048)                │ 32 KB        │
    │ FixedSketch × 8 (10 K samples each)      │ 640 KB       │
    │ ReservoirSampler (1 000 items)           │ ~200 KB      │
    ├──────────────────────────────────────────┼──────────────┤
    │ Typical (50 K unique IPs)                │ ~50 MB       │
    │ Worst-case (500 K cap active)            │ ~250 MB      │
    └──────────────────────────────────────────┴──────────────┘
    """
    t_start = time.monotonic()

    profiles: Dict[str, IPProfile] = {}
    cms      = CountMinSketch(width=2048, depth=4)
    sampler  = ReservoirSampler(size=1000)

    sk_ports    = FixedSketch(SKETCH_SIZE)
    sk_ips      = FixedSketch(SKETCH_SIZE)
    sk_packets  = FixedSketch(SKETCH_SIZE)
    sk_bytes    = FixedSketch(SKETCH_SIZE)
    sk_dns      = FixedSketch(SKETCH_SIZE)
    sk_login    = FixedSketch(SKETCH_SIZE)
    sk_icmp     = FixedSketch(SKETCH_SIZE)
    sk_flowsize = FixedSketch(SKETCH_SIZE)

    total_flows      = 0
    total_bytes      = 0
    capped_ips_count = 0
    min_ts: Optional[datetime] = None
    max_ts: Optional[datetime] = None

    protocol_counts:  Dict[str, int] = defaultdict(int)
    protocol_bytes:   Dict[str, int] = defaultdict(int)
    protocol_packets: Dict[str, int] = defaultdict(int)

    # The floor value from config is used as the large_flow threshold until
    # enough sketch samples accumulate for dynamic() to compute real statistics.
    # This means detection fires from the very first flow — no warmup delay.
    from app.config import FLOOR_FLOWSIZE
    current_flowsize_thresh = FLOOR_FLOWSIZE

    # ── Single streaming pass ─────────────────────────────────────────────────
    for flow in get_disk_stream(filepath):
        ts     = flow["timestamp"]
        src    = flow["source_ip"]
        dst    = flow["destination_ip"]
        dport  = flow["destination_port"]
        sport  = flow["source_port"]
        proto  = flow["protocol"]
        length = flow["length"]

        if ts is not None:
            if min_ts is None or ts < min_ts:
                min_ts = ts
            if max_ts is None or ts > max_ts:
                max_ts = ts

        # CMS always updated — not bounded by cap
        cms.add(src)

        # Profile update / creation
        if src in profiles:
            profiles[src].update(
                dst, dport, sport, proto, length, ts,
                large_flow_threshold=current_flowsize_thresh,
            )
        elif len(profiles) < MAX_TRACKED_IPS:
            profiles[src] = IPProfile()
            profiles[src].update(
                dst, dport, sport, proto, length, ts,
                large_flow_threshold=current_flowsize_thresh,
            )
        else:
            capped_ips_count += 1
            sk_packets.update(1)
            sk_bytes.update(length)

        sk_flowsize.update(length)

        total_flows  += 1
        total_bytes  += length
        protocol_counts[proto]  += 1
        protocol_bytes[proto]   += length
        protocol_packets[proto] += 1

        sampler.add({
            "timestamp":        ts.isoformat() if ts else "",
            "source_ip":        src,
            "destination_ip":   dst,
            "source_port":      sport,
            "destination_port": dport,
            "protocol":         proto,
            "length":           length,
            "info":             flow.get("info", ""),
        })

    if not profiles:
        return _empty_result()

    # ── Build per-IP sketches from profiled IPs ───────────────────────────────
    for ip, p in profiles.items():
        sk_ports.update(len(p.dst_ports))
        sk_ips.update(len(p.dst_ips))
        sk_packets.update(p.packet_count)
        sk_bytes.update(p.byte_count)
        sk_dns.update(p.dns_count)
        sk_login.update(p.login_count)
        sk_icmp.update(len(p.icmp_dst_ips))

    # ── Profile TTL / sliding window ─────────────────────────────────────────
    if PROFILE_TTL_SECS > 0 and max_ts is not None:
        cutoff_ts = max_ts
        expired   = [
            ip for ip, p in profiles.items()
            if p.last_seen is not None
            and (cutoff_ts - p.last_seen).total_seconds() > PROFILE_TTL_SECS
        ]
        for ip in expired:
            del profiles[ip]
        if expired and DEBUG_DETECTION:
            log.debug(
                "Expired stale profiles",
                extra={"count": len(expired), "ttl_secs": PROFILE_TTL_SECS},
            )

    # ── Capture duration ──────────────────────────────────────────────────────
    duration_secs: float = max(
        (max_ts - min_ts).total_seconds() if (min_ts and max_ts) else 1.0,
        1.0,
    )
    short_capture = duration_secs < MIN_DURATION_SECS

    # ── Global thresholds ─────────────────────────────────────────────────────
    base_thresh: Thresholds = compute_thresholds(
        sk_ports, sk_ips, sk_packets, sk_bytes,
        sk_dns, sk_login, sk_icmp, sk_flowsize,
    )
    int_thresh: Thresholds = base_thresh.for_internal()

    if DEBUG_DETECTION:
        log.debug(
            "Computed thresholds",
            extra={
                "external": {
                    "ports": round(base_thresh.ports, 2),
                    "hosts": round(base_thresh.ips, 2),
                    "packets": round(base_thresh.packets, 2),
                    "bytes_MB": round(base_thresh.bytes_ / 1_048_576, 3),
                    "dns": round(base_thresh.dns, 2),
                    "login": round(base_thresh.login, 2),
                    "icmp": round(base_thresh.icmp, 2),
                    "flowsize_MB": round(base_thresh.flowsize / 1_048_576, 3),
                },
                "internal_multiplied": {
                    "ports": round(int_thresh.ports, 2),
                    "packets": round(int_thresh.packets, 2),
                    "bytes_MB": round(int_thresh.bytes_ / 1_048_576, 3),
                    "dns": round(int_thresh.dns, 2),
                },
            },
        )

    # ── Anomaly detection ─────────────────────────────────────────────────────
    alerts  = AlertManager()
    total_unique = max(len(profiles) + capped_ips_count, 1)

    for ip, p in profiles.items():

        # Minimum evidence filter — skip IPs with too little data
        if not p.has_minimum_evidence(MIN_PACKETS_FOR_DETECTION, MIN_FLOWS_FOR_DETECTION):
            if DEBUG_DETECTION:
                log.debug(
                    "[Filter] IP skipped (insufficient evidence)",
                    extra={
                        "ip": ip,
                        "packets": p.packet_count,
                        "flows": p.flow_count,
                        "min_packets": MIN_PACKETS_FOR_DETECTION,
                        "min_flows": MIN_FLOWS_FOR_DETECTION,
                    },
                )
            continue

        # Select threshold set based on whether source IP is RFC-1918
        thresh = int_thresh if is_private_ip(ip) else base_thresh

        port_scan.evaluate(ip, p, thresh, alerts)
        horizontal_scan.evaluate(ip, p, thresh, alerts)
        dns_tunnel.evaluate(ip, p, thresh, alerts)
        brute_force.evaluate(ip, p, thresh, alerts)
        traffic_flood.evaluate_flood(ip, p, thresh, alerts, short_capture, total_bytes)
        traffic_flood.evaluate_large_flow(ip, p, thresh, alerts)
        traffic_flood.evaluate_heavy_hitter(
            ip, p, cms, thresh, alerts, total_flows, total_unique
        )

    top_talkers = sorted(
        [{"ip": ip, "bytes": p.byte_count, "flows": p.flow_count}
         for ip, p in profiles.items()],
        key=lambda x: x["bytes"],
        reverse=True,
    )[:5]

    elapsed = time.monotonic() - t_start
    log.info(
        "Detection complete",
        extra={
            "total_flows":  total_flows,
            "unique_ips":   len(profiles),
            "capped_ips":   capped_ips_count,
            "anomalies":    len(alerts.anomalies),
            "elapsed_s":    round(elapsed, 3),
        },
    )

    return {
        "summary": {
            "total_flows":             total_flows,
            "total_packets":           total_flows,
            "total_bytes":             total_bytes,
            "unique_src_ips":          len(profiles),
            "capped_ips_not_profiled": capped_ips_count,
            "duration":                f"{duration_secs:.1f}s",
            "short_capture_warning":   short_capture,
            "avg_flow_size":           round(total_bytes / total_flows, 2) if total_flows else 0,
            "analysis_time_secs":      round(elapsed, 3),
            "thresholds_used": {
                "port_scan_ports":  round(base_thresh.ports,    2),
                "horiz_scan_ips":   round(base_thresh.ips,      2),
                "flood_packets":    round(base_thresh.packets,  2),
                "exfil_bytes_mb":   round(base_thresh.bytes_   / 1_048_576, 3),
                "dns_queries":      round(base_thresh.dns,      2),
                "login_conns":      round(base_thresh.login,    2),
                "icmp_dsts":        round(base_thresh.icmp,     2),
                "large_flow_mb":    round(base_thresh.flowsize / 1_048_576, 3),
            },
        },
        "protocol_distribution":         dict(protocol_counts),
        "protocol_bytes_distribution":   dict(protocol_bytes),
        "protocol_packets_distribution": dict(protocol_packets),
        "flows":       sampler.samples,
        "anomalies":   alerts.anomalies,
        "top_talkers": top_talkers,
    }


def _empty_result() -> dict:
    return {
        "summary": {
            "total_flows": 0, "total_packets": 0, "total_bytes": 0,
            "unique_src_ips": 0, "capped_ips_not_profiled": 0,
            "duration": "0s", "short_capture_warning": False,
            "avg_flow_size": 0, "analysis_time_secs": 0,
            "thresholds_used": {},
        },
        "protocol_distribution":         {},
        "protocol_bytes_distribution":   {},
        "protocol_packets_distribution": {},
        "flows":       [],
        "anomalies":   [],
        "top_talkers": [],
    }
