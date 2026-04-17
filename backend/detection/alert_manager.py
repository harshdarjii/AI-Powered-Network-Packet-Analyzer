"""
DeepTrace — AlertManager

Handles anomaly deduplication (same IP + type → highest severity wins)
and per-IP per-rule cooldown (suppresses repeated alerts within a window).
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.config import ALERT_COOLDOWN_SECS

_SEV_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


class AlertManager:
    def __init__(self, cooldown_secs: float = ALERT_COOLDOWN_SECS) -> None:
        self._anomalies:    List[dict]              = []
        self._dedup:        Dict[Tuple[str, str], int] = {}   # (ip, type) → list index
        self._cooldown:     Dict[Tuple[str, str], float] = {} # (ip, type) → last_seen epoch
        self._cooldown_secs = cooldown_secs

    def flag(
        self,
        type_:  str,
        sev:    str,
        desc:   str,
        source: str,
        tinfo:  str = "",
    ) -> None:
        """
        Record an anomaly with deduplication + cooldown.

        • Same (IP, type) pair → keep only highest severity.
        • Repeat alerts within cooldown window → suppressed.
        """
        key       = (source, type_)
        now       = time.monotonic()
        last_seen = self._cooldown.get(key)

        if last_seen is not None and (now - last_seen) < self._cooldown_secs:
            # Cooldown active — update severity in place if higher, but don't
            # add a new entry.
            if key in self._dedup:
                existing = self._anomalies[self._dedup[key]]
                if _SEV_RANK.get(sev, 0) > _SEV_RANK.get(existing["severity"], 0):
                    existing["severity"]    = sev
                    existing["description"] = f"{desc} {tinfo}".strip()
            return

        self._cooldown[key] = now

        if key in self._dedup:
            existing = self._anomalies[self._dedup[key]]
            if _SEV_RANK.get(sev, 0) > _SEV_RANK.get(existing["severity"], 0):
                existing["severity"]    = sev
                existing["description"] = f"{desc} {tinfo}".strip()
            return

        self._dedup[key] = len(self._anomalies)
        self._anomalies.append({
            "id":          str(uuid.uuid4()),
            "type":        type_,
            "severity":    sev,
            "description": f"{desc} {tinfo}".strip(),
            "source":      source,
            "timestamp":   datetime.now(timezone.utc).isoformat(),
        })

    @property
    def anomalies(self) -> List[dict]:
        return self._anomalies

    def confidence(self, value: float, threshold: float) -> str:
        if threshold <= 0:
            return "Low"
        r = value / threshold
        if r >= 5.0: return "Critical"
        if r >= 3.0: return "High"
        if r >= 1.5: return "Medium"
        return "Low"
