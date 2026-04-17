"""
DeepTrace — File Streamer
Routes a file path to the correct disk-streaming parser.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ingestion.parsers.csv_parser import stream_csv_from_disk
from ingestion.parsers.pcap_parser import stream_pcap_from_disk
from ingestion.parsers.pcapng_parser import stream_pcapng_from_disk


def get_disk_stream(filepath: Path) -> Iterator[dict]:
    suffix = filepath.suffix.lower()
    if suffix == ".csv":
        return stream_csv_from_disk(filepath)
    elif suffix == ".pcap":
        return stream_pcap_from_disk(filepath)
    elif suffix == ".pcapng":
        return stream_pcapng_from_disk(filepath)
    return iter([])
