"""
DeepTrace — Threshold Computation

Computes per-metric dynamic thresholds from FixedSketch samples.
Applies internal-IP multipliers to reduce false positives on RFC-1918 hosts.
"""
from __future__ import annotations

from dataclasses import dataclass

from analytics.sketches.fixed_sketch import FixedSketch
from app.config import (
    FLOOR_PORTS, FLOOR_HOSTS, FLOOR_PACKETS, FLOOR_BYTES,
    FLOOR_DNS, FLOOR_LOGIN, FLOOR_ICMP, FLOOR_FLOWSIZE,
    INTERNAL_PORTS_MULT, INTERNAL_PACKETS_MULT,
    INTERNAL_BYTES_MULT, INTERNAL_DNS_MULT,
    MIN_SKETCH_SAMPLES,
)


@dataclass
class Thresholds:
    ports:    float
    ips:      float
    packets:  float
    bytes_:   float
    dns:      float
    login:    float
    icmp:     float
    flowsize: float

    def for_internal(self) -> "Thresholds":
        """Return a copy with thresholds multiplied for internal / RFC-1918 hosts."""
        return Thresholds(
            ports    = self.ports    * INTERNAL_PORTS_MULT,
            ips      = self.ips      * INTERNAL_PORTS_MULT,
            packets  = self.packets  * INTERNAL_PACKETS_MULT,
            bytes_   = self.bytes_   * INTERNAL_BYTES_MULT,
            dns      = self.dns      * INTERNAL_DNS_MULT,
            login    = self.login    * INTERNAL_PACKETS_MULT,
            icmp     = self.icmp     * INTERNAL_PORTS_MULT,
            flowsize = self.flowsize * INTERNAL_BYTES_MULT,
        )


def compute_thresholds(
    sk_ports:    FixedSketch,
    sk_ips:      FixedSketch,
    sk_packets:  FixedSketch,
    sk_bytes:    FixedSketch,
    sk_dns:      FixedSketch,
    sk_login:    FixedSketch,
    sk_icmp:     FixedSketch,
    sk_flowsize: FixedSketch,
) -> Thresholds:
    """
    Compute all dynamic thresholds from sketch samples.
    IQR multipliers and Z-score parameters are intentionally conservative
    (higher than v6.1) to reduce false positives on benign traffic.
    """
    return Thresholds(
        ports    = sk_ports.dynamic(iqr_mult=2.0, z=3.0, floor=FLOOR_PORTS,    min_samples=MIN_SKETCH_SAMPLES),
        ips      = sk_ips.dynamic(iqr_mult=2.0,   z=3.0, floor=FLOOR_HOSTS,    min_samples=MIN_SKETCH_SAMPLES),
        packets  = sk_packets.dynamic(iqr_mult=2.0, z=3.0, floor=FLOOR_PACKETS, min_samples=MIN_SKETCH_SAMPLES),
        bytes_   = sk_bytes.dynamic(iqr_mult=2.5,  z=3.5, floor=FLOOR_BYTES,   min_samples=MIN_SKETCH_SAMPLES),
        dns      = sk_dns.dynamic(iqr_mult=2.0,    z=3.0, floor=FLOOR_DNS,     min_samples=MIN_SKETCH_SAMPLES),
        login    = sk_login.dynamic(iqr_mult=2.0,  z=3.0, floor=FLOOR_LOGIN,   min_samples=MIN_SKETCH_SAMPLES),
        icmp     = sk_icmp.dynamic(iqr_mult=2.0,   z=3.0, floor=FLOOR_ICMP,    min_samples=MIN_SKETCH_SAMPLES),
        flowsize = sk_flowsize.dynamic(iqr_mult=3.5, z=4.5, floor=FLOOR_FLOWSIZE, min_samples=MIN_SKETCH_SAMPLES),
    )