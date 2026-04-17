"""
DeepTrace — /api/analyze endpoint
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import RATE_LIMIT_ANALYZE
from app.logging_config import log
from detection.anomaly_engine import run_detection_from_disk
from ingestion.upload_handler import _cleanup_file, save_upload_to_disk

router  = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/analyze")
@limiter.limit(RATE_LIMIT_ANALYZE)
async def analyze_file(
    request: Request,
    file:    UploadFile = File(...),
) -> dict:
    """
    Zero-RAM analysis endpoint.
    Upload streamed to disk → detection in thread pool → temp file deleted.
    """
    fname = (file.filename or "").lower()
    if not any(fname.endswith(ext) for ext in (".csv", ".pcap", ".pcapng")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use .csv, .pcap, or .pcapng",
        )

    tmp_path: Path = await save_upload_to_disk(file)

    try:
        from app.main import _EXECUTOR
        loop   = asyncio.get_running_loop()
        result = await loop.run_in_executor(_EXECUTOR, run_detection_from_disk, tmp_path)
    except asyncio.CancelledError:
        log.info("Analysis cancelled by client")
        raise
    except Exception as exc:
        log.error("Detection failed", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        _cleanup_file(tmp_path)

    return result
