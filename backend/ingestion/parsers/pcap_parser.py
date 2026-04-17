"""
DeepTrace — PCAP Parser
Packet-by-packet streaming via raw struct parsing.
incl_len clamped to snaplen — guards against malformed captures.
"""
from __future__ import annotations

import struct
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from app.logging_config import log

_PROTO_MAP = {1: "ICMP", 6: "TCP", 17: "UDP", 47: "GRE", 50: "ESP", 58: "ICMPv6"}


def _unpack_ipv4(data: bytes, offset: int) -> str:
    return (
        f"{data[offset]}.{data[offset+1]}."
        f"{data[offset+2]}.{data[offset+3]}"
    )


def stream_pcap_from_disk(filepath: Path) -> Iterator[dict]:
    with open(filepath, "rb", buffering=256 * 1024) as fh:
        global_hdr = fh.read(24)
        if len(global_hdr) < 24:
            return

        magic = struct.unpack_from("<I", global_hdr, 0)[0]
        if magic == 0xA1B2C3D4:
            endian = "<"
        elif magic == 0xD4C3B2A1:
            endian = ">"
        else:
            log.warning("Invalid PCAP magic bytes — skipping file")
            return

        _, _, _, _, snaplen, _, network = struct.unpack_from(endian + "IHHiIII", global_hdr, 0)
        max_pkt = snaplen if 0 < snaplen <= 262144 else 65535

        while True:
            rec_hdr = fh.read(16)
            if len(rec_hdr) < 16:
                break

            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(endian + "IIII", rec_hdr)
            incl_len = min(incl_len, max_pkt)

            pkt_data = fh.read(incl_len)
            if len(pkt_data) < incl_len:
                break

            try:
                ts: Optional[datetime] = datetime.fromtimestamp(ts_sec + ts_usec / 1_000_000)
            except (OSError, ValueError, OverflowError):
                ts = None

            src_ip = dst_ip = "0.0.0.0"
            src_port = dst_port = 0
            proto = "OTHER"

            try:
                if network == 1 and len(pkt_data) >= 14:
                    eth_type = struct.unpack_from(">H", pkt_data, 12)[0]

                    if eth_type == 0x0800 and len(pkt_data) >= 34:
                        ip_start  = 14
                        ihl       = (pkt_data[ip_start] & 0x0F) * 4
                        proto_num = pkt_data[ip_start + 9]

                        if ip_start + 20 > len(pkt_data):
                            yield {
                                "timestamp": ts, "source_ip": "0.0.0.0",
                                "destination_ip": "0.0.0.0", "source_port": 0,
                                "destination_port": 0, "protocol": "TRUNCATED",
                                "length": orig_len, "info": "",
                            }
                            continue

                        src_ip = _unpack_ipv4(pkt_data, ip_start + 12)
                        dst_ip = _unpack_ipv4(pkt_data, ip_start + 16)
                        proto  = _PROTO_MAP.get(proto_num, f"PROTO_{proto_num}")

                        l4 = ip_start + ihl
                        if proto_num in (6, 17) and l4 + 4 <= len(pkt_data):
                            src_port = struct.unpack_from(">H", pkt_data, l4)[0]
                            dst_port = struct.unpack_from(">H", pkt_data, l4 + 2)[0]
                            if proto_num == 6:
                                proto = (
                                    "HTTP"  if dst_port in (80, 8080) or src_port in (80, 8080)
                                    else "HTTPS" if dst_port == 443 or src_port == 443
                                    else "TCP"
                                )
                            else:
                                proto = "DNS" if dst_port == 53 or src_port == 53 else "UDP"

                    elif eth_type == 0x0806:
                        proto = "ARP"

            except Exception:
                pass

            yield {
                "timestamp":        ts,
                "source_ip":        src_ip,
                "destination_ip":   dst_ip,
                "source_port":      src_port,
                "destination_port": dst_port,
                "protocol":         proto,
                "length":           orig_len,
                "info":             "",
            }
