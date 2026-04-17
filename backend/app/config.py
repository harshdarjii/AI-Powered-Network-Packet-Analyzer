"""
DeepTrace v7.0 — Centralised Configuration
All tuneable values read from DEEPTRACE_* environment variables.
"""
from __future__ import annotations

import os
from pathlib import Path


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ[key])
    except (KeyError, ValueError):
        return default


def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ[key])
    except (KeyError, ValueError):
        return default


# ── Storage ───────────────────────────────────────────────────────────────────
UPLOAD_DIR: Path = Path(
    os.environ.get("DEEPTRACE_UPLOAD_DIR", "./deeptrace_uploads")
).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Upload limits ─────────────────────────────────────────────────────────────
MAX_UPLOAD_BYTES:   int   = _env_int("DEEPTRACE_MAX_UPLOAD_BYTES",   2 * 1024 ** 3)  # 2 GB
MAX_TRACKED_IPS:    int   = _env_int("DEEPTRACE_MAX_TRACKED_IPS",    500_000)
UPLOAD_CHUNK_BYTES: int   = _env_int("DEEPTRACE_UPLOAD_CHUNK_BYTES", 1024 * 1024)    # 1 MB
MIN_DURATION_SECS:  float = _env_float("DEEPTRACE_MIN_DURATION_SECS", 5.0)

# ── Concurrency ───────────────────────────────────────────────────────────────
WORKER_THREADS: int = _env_int("DEEPTRACE_WORKERS", min(4, (os.cpu_count() or 2)))

# ── AI / Ollama ───────────────────────────────────────────────────────────────
OLLAMA_BASE_URL:   str   = os.environ.get("DEEPTRACE_OLLAMA_URL",       "http://localhost:11434")
AI_TIMEOUT_SECS:   float = _env_float("DEEPTRACE_AI_TIMEOUT",           90.0)
AI_MAX_RETRIES:    int   = _env_int("DEEPTRACE_AI_MAX_RETRIES",          3)
AI_ANALYSIS_MODEL: str   = os.environ.get("DEEPTRACE_AI_MODEL",         "llama3:8b")
AI_EXPLAIN_MODEL:  str   = os.environ.get("DEEPTRACE_AI_EXPLAIN_MODEL", "llama3:8b")
AI_MAX_ANOMALIES:  int   = _env_int("DEEPTRACE_AI_MAX_ANOMALIES",        50)

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_ANALYZE: str = os.environ.get("DEEPTRACE_RATE_LIMIT", "10/minute")

# ── Sketches ──────────────────────────────────────────────────────────────────
SKETCH_SIZE: int = _env_int("DEEPTRACE_SKETCH_SIZE", 10_000)

# ── Detection: known login ports ──────────────────────────────────────────────
LOGIN_PORTS: frozenset = frozenset({21, 22, 23, 445, 3389})

# ── Detection: adaptive threshold stability guard ────────────────────────────
# A sketch must have at least this many samples before its dynamic() method
# computes real statistics. Below this count it simply returns the floor value,
# which is a safe conservative default. This replaces the old warmup phase —
# thresholds become progressively more accurate as more data arrives, and
# detection fires from the very first flow (using floor values initially).
MIN_SKETCH_SAMPLES: int = _env_int("DEEPTRACE_MIN_SKETCH_SAMPLES", 50)

# ── Detection: minimum evidence ───────────────────────────────────────────────
# An IP must meet BOTH criteria before any rule is evaluated against it.
MIN_PACKETS_FOR_DETECTION: int   = _env_int("DEEPTRACE_MIN_PACKETS",  20)
MIN_FLOWS_FOR_DETECTION:   int   = _env_int("DEEPTRACE_MIN_FLOWS",    10)

# ── Detection: sliding window / profile TTL ───────────────────────────────────
# Profiles whose last_seen is older than this are discarded at the end of
# a streaming pass.  Set to 0 to disable expiry.
PROFILE_TTL_SECS: float = _env_float("DEEPTRACE_PROFILE_TTL", 300.0)  # 5 minutes

# ── Detection: alert cooldown (seconds per IP per rule type) ──────────────────
ALERT_COOLDOWN_SECS: float = _env_float("DEEPTRACE_ALERT_COOLDOWN", 60.0)

# ── Detection: threshold floors (increased vs v6.1 to cut false positives) ────
FLOOR_PORTS:     float = _env_float("DEEPTRACE_FLOOR_PORTS",     20.0)
FLOOR_HOSTS:     float = _env_float("DEEPTRACE_FLOOR_HOSTS",     20.0)
FLOOR_PACKETS:   float = _env_float("DEEPTRACE_FLOOR_PACKETS",   30.0)
FLOOR_BYTES:     float = _env_float("DEEPTRACE_FLOOR_BYTES",     100_000.0)
FLOOR_DNS:       float = _env_float("DEEPTRACE_FLOOR_DNS",       30.0)
FLOOR_LOGIN:     float = _env_float("DEEPTRACE_FLOOR_LOGIN",     10.0)
FLOOR_ICMP:      float = _env_float("DEEPTRACE_FLOOR_ICMP",      10.0)
FLOOR_FLOWSIZE:  float = _env_float("DEEPTRACE_FLOOR_FLOWSIZE",  2_000_000.0)

# ── Detection: internal-IP threshold multipliers ──────────────────────────────
# Private (RFC-1918) hosts legitimately generate more traffic.
# Thresholds for internal IPs are multiplied by these factors.
INTERNAL_PORTS_MULT:   float = _env_float("DEEPTRACE_INT_PORTS_MULT",   2.0)
INTERNAL_PACKETS_MULT: float = _env_float("DEEPTRACE_INT_PACKETS_MULT", 3.0)
INTERNAL_BYTES_MULT:   float = _env_float("DEEPTRACE_INT_BYTES_MULT",   3.0)
INTERNAL_DNS_MULT:     float = _env_float("DEEPTRACE_INT_DNS_MULT",     2.0)

# ── Detection: large-flow repetition guard ────────────────────────────────────
# An "oversized flow" anomaly fires only when the same source IP has been
# seen with large flows at least LARGE_FLOW_MIN_REPEAT times.
LARGE_FLOW_MIN_REPEAT: int = _env_int("DEEPTRACE_LARGE_FLOW_REPEAT", 3)

# ── Detection: multi-signal minimum requirements ──────────────────────────────
PORTSCAN_MIN_PACKETS:   int   = _env_int("DEEPTRACE_PS_MIN_PKTS",   40)
PORTSCAN_MIN_DURATION:  float = _env_float("DEEPTRACE_PS_MIN_DUR",  10.0)
BRUTEFORCE_MIN_PACKETS: int   = _env_int("DEEPTRACE_BF_MIN_PKTS",   30)
DNS_MIN_FLOWS:          int   = _env_int("DEEPTRACE_DNS_MIN_FLOWS",  20)
DNS_FRAC_THRESHOLD:     float = _env_float("DEEPTRACE_DNS_FRAC",     0.40)
BRUTEFORCE_FRAC:        float = _env_float("DEEPTRACE_BF_FRAC",      0.20)
HORIZ_MIN_PACKETS:      int   = _env_int("DEEPTRACE_HORIZ_MIN_PKTS", 30)

# ── Debug mode ────────────────────────────────────────────────────────────────
DEBUG_DETECTION: bool = os.environ.get("DEEPTRACE_DEBUG", "").lower() in ("1", "true", "yes")
