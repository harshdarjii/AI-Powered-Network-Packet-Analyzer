"""
DeepTrace — PCAPng Parser (requires Scapy).
Yields nothing if Scapy is not installed — keeps the function a proper generator.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterator

from app.logging_config import log


def stream_pcapng_from_disk(filepath: Path) -> Iterator[dict]:
    try:
        from scapy.all import PcapNgReader, IP, TCP, UDP, ICMP  # type: ignore
    except ImportError:
        log.warning("Scapy not installed — PCAPng files will not be parsed")
        yield from ()
        return

    with PcapNgReader(str(filepath)) as reader:
        for pkt in reader:
            try:
                if IP not in pkt:
                    continue
                length = len(pkt)
                sp = dp = 0
                proto   = "OTHER"
                if TCP in pkt:
                    sp, dp = pkt[TCP].sport, pkt[TCP].dport
                    proto  = (
                        "HTTP"  if dp in (80, 8080) or sp in (80, 8080)
                        else "HTTPS" if dp == 443 or sp == 443
                        else "TCP"
                    )
                elif UDP in pkt:
                    sp, dp = pkt[UDP].sport, pkt[UDP].dport
                    proto  = "DNS" if dp == 53 or sp == 53 else "UDP"
                elif ICMP in pkt:
                    proto = "ICMP"

                yield {
                    "timestamp":        datetime.fromtimestamp(float(pkt.time)),
                    "source_ip":        pkt[IP].src,
                    "destination_ip":   pkt[IP].dst,
                    "source_port":      sp,
                    "destination_port": dp,
                    "protocol":         proto,
                    "length":           length,
                    "info":             "",
                }
            except Exception:
                continue
