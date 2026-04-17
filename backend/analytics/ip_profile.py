"""
DeepTrace — IPProfile: per-source-IP behavioural aggregate.

__slots__ keeps each instance to ~450 bytes.
large_flow_count tracks how many oversized single packets this IP sent,
enabling the repetition guard in the large-flow detection rule.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from app.config import LOGIN_PORTS


class IPProfile:
    __slots__ = (
        "packet_count", "byte_count", "flow_count",
        "dst_ports", "dst_ips",
        "dns_count", "login_count", "icmp_dst_ips",
        "large_flow_count",
        "first_seen", "last_seen",
    )

    def __init__(self) -> None:
        self.packet_count:    int               = 0
        self.byte_count:      int               = 0
        self.flow_count:      int               = 0
        self.dst_ports:       set               = set()
        self.dst_ips:         set               = set()
        self.dns_count:       int               = 0
        self.login_count:     int               = 0
        self.icmp_dst_ips:    set               = set()
        self.large_flow_count: int              = 0      # repetition guard
        self.first_seen:      Optional[datetime] = None
        self.last_seen:       Optional[datetime] = None

    def update(
        self,
        dst_ip:    str,
        dst_port:  int,
        src_port:  int,
        proto:     str,
        length:    int,
        ts:        Optional[datetime],
        large_flow_threshold: float = 0.0,
    ) -> None:
        self.packet_count += 1
        self.byte_count   += length
        self.flow_count   += 1
        self.dst_ports.add(dst_port)
        self.dst_ips.add(dst_ip)

        if ts is not None:
            if self.first_seen is None or ts < self.first_seen:
                self.first_seen = ts
            if self.last_seen is None or ts > self.last_seen:
                self.last_seen = ts

        if proto == "DNS" or dst_port == 53 or src_port == 53:
            self.dns_count += 1
        if dst_port in LOGIN_PORTS:
            self.login_count += 1
        if proto == "ICMP":
            self.icmp_dst_ips.add(dst_ip)
        if large_flow_threshold > 0 and length >= large_flow_threshold:
            self.large_flow_count += 1

    @property
    def duration_secs(self) -> float:
        if self.first_seen and self.last_seen:
            try:
                return max((self.last_seen - self.first_seen).total_seconds(), 1.0)
            except Exception:
                pass
        return 1.0

    @property
    def pps(self) -> float:
        return self.packet_count / self.duration_secs

    def has_minimum_evidence(
        self,
        min_packets: int,
        min_flows:   int,
    ) -> bool:
        """
        Returns True only when this IP has enough traffic data to be
        meaningfully analysed.  Prevents single-packet noise from triggering
        anomalies.
        """
        return (
            self.packet_count >= min_packets
            and self.flow_count >= min_flows
        )
