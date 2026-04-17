"""
DeepTrace — /api/insights endpoint
"""
from __future__ import annotations

from fastapi import APIRouter

from ai.insights_engine import get_insights

router = APIRouter()


@router.post("/api/insights")
async def insights(data: dict) -> dict:
    """AI insight layer — wraps Ollama with retry, fallback, and validation."""
    return await get_insights(data)
