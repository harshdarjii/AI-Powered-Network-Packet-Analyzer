"""
DeepTrace — CSV Parser
Streams rows one at a time; uses manual csv.reader (faster than DictReader).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterator, List

from utils.time_utils import parse_timestamp
from utils.validation import sanitise_csv_field


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def stream_csv_from_disk(filepath: Path) -> Iterator[dict]:
    with open(filepath, "r", encoding="utf-8", errors="replace", buffering=256 * 1024) as fh:
        reader = csv.reader(fh)
        try:
            raw_headers = next(reader)
        except StopIteration:
            return

        headers = [h.lower().strip() for h in raw_headers]

        def col_idx(*candidates: str) -> int:
            for c in candidates:
                try:
                    return headers.index(c)
                except ValueError:
                    pass
            return -1

        i_proto = col_idx("protocol")
        i_len   = col_idx("length", "bytes", "packet_size")
        i_ts    = col_idx("time", "timestamp")
        i_src   = col_idx("source", "src", "source_ip", "src_ip")
        i_dst   = col_idx("destination", "dst", "destination_ip", "dst_ip")
        i_sport = col_idx("src port", "source_port")
        i_dport = col_idx("dst port", "destination_port")
        i_info  = col_idx("info", "tcp_flags", "label")

        def get(row: List[str], idx: int, default: Any = "") -> Any:
            if idx < 0 or idx >= len(row):
                return default
            v = row[idx].strip()
            return v if v else default

        for row in reader:
            if not row:
                continue

            proto = sanitise_csv_field(
                str(get(row, i_proto, "UNKNOWN"))
            ).upper().strip()

            yield {
                "timestamp":        parse_timestamp(str(get(row, i_ts, ""))),
                "source_ip":        sanitise_csv_field(str(get(row, i_src,   "0.0.0.0"))),
                "destination_ip":   sanitise_csv_field(str(get(row, i_dst,   "0.0.0.0"))),
                "source_port":      _safe_int(get(row, i_sport, 0)),
                "destination_port": _safe_int(get(row, i_dport, 0)),
                "protocol":         proto,
                "length":           _safe_int(get(row, i_len, 0)),
                "info":             sanitise_csv_field(str(get(row, i_info, ""))),
            }
