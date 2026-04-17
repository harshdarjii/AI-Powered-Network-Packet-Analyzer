"""
DeepTrace — Main Application Entry Point

Architecture:
    Upload  → Disk (chunked write, never in RAM)
    Disk    → Stream parser (one packet/row at a time)
    Flow    → IPProfile aggregator  +  CountMinSketch heavy-hitter
    Profiles→ FixedSketch dynamic threshold computation
    Profiles→ Multi-signal anomaly detection + deduplication + cooldown
    Results → Response (anomalies + 1 000 reservoir-sampled flows)

Key improvements:
  • Adaptive thresholds — floor values used until 50+ sketch samples collected,
    then real statistics kick in automatically (replaces old warmup phase)
  • Detection fires from the very first flow — no dead zone
  • Minimum evidence filter (low-traffic IPs ignored)
  • Multi-signal detection rules (all rules need ≥2 corroborating signals)
  • Internal-IP aware thresholds (RFC-1918 hosts get higher thresholds)
  • Profile TTL / sliding window (stale profiles discarded)
  • Alert cooldown (one alert per IP per rule per 60 s)
  • Oversized flow repetition guard (single download ≠ alert)
  • Fully modular codebase
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import WORKER_THREADS, UPLOAD_DIR
from app.logging_config import log

# Executor is module-level so api/analyze_endpoint.py can import it.
_EXECUTOR: ThreadPoolExecutor


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _EXECUTOR
    _EXECUTOR = ThreadPoolExecutor(max_workers=WORKER_THREADS)
    log.info(
        "DeepTrace v7.1 started",
        extra={"workers": WORKER_THREADS, "upload_dir": str(UPLOAD_DIR)},
    )
    yield
    _EXECUTOR.shutdown(wait=True, cancel_futures=False)
    log.info("Executor shut down cleanly")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="DeepTrace Network Forensics API",
    version="7.1",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
from api.analyze_endpoint  import router as analyze_router   # noqa: E402
from api.insights_endpoint import router as insights_router  # noqa: E402

app.include_router(analyze_router)
app.include_router(insights_router)


# ── Status endpoint ───────────────────────────────────────────────────────────
@app.get("/status")
async def get_status() -> dict:
    from app.config import (
        MAX_UPLOAD_BYTES, MAX_TRACKED_IPS, RATE_LIMIT_ANALYZE,
        MIN_SKETCH_SAMPLES, MIN_PACKETS_FOR_DETECTION, MIN_FLOWS_FOR_DETECTION,
        PROFILE_TTL_SECS, ALERT_COOLDOWN_SECS, DEBUG_DETECTION,
        FLOOR_PORTS, FLOOR_HOSTS, FLOOR_PACKETS, FLOOR_DNS,
    )
    return {
        "status":  "online",
        "version": "7.1",
        "engine":  "DeepTrace Zero-RAM Streaming",
        "upload_dir": str(UPLOAD_DIR),
        "workers":    WORKER_THREADS,
        "detection": {
            "min_sketch_samples":    MIN_SKETCH_SAMPLES,
            "min_packets":           MIN_PACKETS_FOR_DETECTION,
            "min_flows":             MIN_FLOWS_FOR_DETECTION,
            "profile_ttl_secs":      PROFILE_TTL_SECS,
            "alert_cooldown_secs":   ALERT_COOLDOWN_SECS,
            "debug_mode":            DEBUG_DETECTION,
            "threshold_floors": {
                "ports":   FLOOR_PORTS,
                "hosts":   FLOOR_HOSTS,
                "packets": FLOOR_PACKETS,
                "dns":     FLOOR_DNS,
            },
        },
        "limits": {
            "max_upload_bytes": MAX_UPLOAD_BYTES,
            "max_tracked_ips":  MAX_TRACKED_IPS,
            "rate_limit":       RATE_LIMIT_ANALYZE,
        },
    }


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.environ.get("DEEPTRACE_HOST", "0.0.0.0"),
        port=int(os.environ.get("DEEPTRACE_PORT", "8000")),
        workers=1,
        log_config=None,
    )