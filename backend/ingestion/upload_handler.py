"""
DeepTrace — Upload Handler
Streams uploads to disk: path-safe, MIME-validated, size-limited.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from app.config import UPLOAD_DIR, MAX_UPLOAD_BYTES, UPLOAD_CHUNK_BYTES
from app.logging_config import log
from utils.validation import validate_mime, safe_filename


async def save_upload_to_disk(upload: UploadFile) -> Path:
    """
    Stream the upload to a uniquely-named temp file on disk.
    Partial file is always removed on any error path.
    """
    s_name   = safe_filename(upload.filename or "upload")
    ext      = Path(s_name).suffix.lower()
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    written  = 0
    first    = True

    try:
        async with aiofiles.open(tmp_path, "wb") as out:
            while True:
                chunk = await upload.read(UPLOAD_CHUNK_BYTES)
                if not chunk:
                    break

                if first:
                    validate_mime(chunk[:8], ext)
                    first = False

                written += len(chunk)
                if written > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Upload exceeds maximum allowed size of "
                            f"{MAX_UPLOAD_BYTES / 1024 ** 3:.1f} GB."
                        ),
                    )
                await out.write(chunk)

        log.info("Upload saved", extra={"path": str(tmp_path), "bytes": written})
        return tmp_path

    except (HTTPException, asyncio.CancelledError):
        _cleanup_file(tmp_path)
        raise
    except Exception as exc:
        _cleanup_file(tmp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc


def _cleanup_file(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass
