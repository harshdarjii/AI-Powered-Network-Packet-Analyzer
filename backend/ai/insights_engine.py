"""
DeepTrace — AI Insights Engine

Fully async Ollama integration with:
  • retry + exponential back-off
  • robust JSON extraction (brace-scan)
  • field validation
  • structured fallback on any failure
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional

import httpx

from ai.prompt_builder import build_analysis_prompt
from app.config import (
    OLLAMA_BASE_URL, AI_TIMEOUT_SECS, AI_MAX_RETRIES,
    AI_ANALYSIS_MODEL, AI_MAX_ANOMALIES,
)
from app.logging_config import log

_SEV_RANK_AI = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


# ── JSON extraction ───────────────────────────────────────────────────────────

def _extract_json(text: str) -> Optional[dict]:
    first = text.find("{")
    last  = text.rfind("}")
    if first == -1 or last <= first:
        return None
    candidate = text[first: last + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        candidate = re.sub(r"//[^\n]*",    "",    candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None


# ── Field validation ──────────────────────────────────────────────────────────

def _infer_risk(detected_types: List[str]) -> str:
    lower = {t.lower() for t in detected_types}
    if lower & {"traffic flooding", "heavy-hitter traffic"}:
        return "Critical"
    if lower & {
        "vertical port scan", "horizontal scan",
        "possible brute force", "possible dns tunneling",
    }:
        return "High"
    if lower & {
        "data exfiltration suspicion", "icmp sweep",
        "repeated oversized flows",
    }:
        return "Medium"
    return "Low"


def _sanitise_attack_types(items: List[Any]) -> List[str]:
    cleaned = []
    for item in items:
        if not isinstance(item, str):
            continue
        s = item.strip()
        if 3 <= len(s) <= 60:
            cleaned.append(s)
    return cleaned or ["Unknown"]


def _validate_ai_fields(parsed: dict, detected_types: List[str]) -> dict:
    for k in ["executive_summary", "attack_story", "technical_analysis",
              "plain_english_explanation", "risk_impact",
              "confidence_reasoning", "risk_level"]:
        if not isinstance(parsed.get(k), str):
            parsed[k] = ""

    for k in ["likely_attack_types", "immediate_actions", "long_term_prevention"]:
        if not isinstance(parsed.get(k), list):
            parsed[k] = []

    if parsed["risk_level"] not in {"Low", "Medium", "High", "Critical"}:
        parsed["risk_level"] = _infer_risk(detected_types)

    parsed["likely_attack_types"] = _sanitise_attack_types(
        parsed.get("likely_attack_types", [])
    )
    return parsed


def _fill_empty_fields(parsed: dict, anomalies: List[dict], detected_types: List[str]) -> dict:
    """
    If the AI left any field empty, fill it with a sensible rule-based value
    derived from the actual anomaly data. This ensures the response is always
    useful even when the model produces thin output.
    """
    # Build a plain-text anomaly summary for fallback strings
    lines = []
    for a in anomalies[:10]:
        lines.append(f"- {a.get('type','?')} ({a.get('severity','?')}): {a.get('description','')}")
    anomaly_text = "\n".join(lines) if lines else "No anomalies."

    risk = parsed.get("risk_level", "Low")

    if not parsed.get("executive_summary", "").strip():
        parsed["executive_summary"] = (
            f"DeepTrace detected {len(anomalies)} anomalies in the network capture. "
            f"Detected threat types include: {', '.join(detected_types) or 'unknown'}. "
            f"Overall risk is assessed as {risk}."
        )

    if not parsed.get("attack_story", "").strip():
        parsed["attack_story"] = (
            f"Based on the detected anomalies, the following activity was observed:\n{anomaly_text}\n"
            f"This pattern suggests malicious or abnormal network behaviour warranting investigation."
        )

    if not parsed.get("technical_analysis", "").strip():
        parsed["technical_analysis"] = (
            f"Rule-based detection identified the following anomaly types: "
            f"{', '.join(detected_types) or 'none'}. "
            f"Full details are available in the anomalies list. "
            f"Each anomaly was triggered only after passing multi-signal evidence thresholds."
        )

    if not parsed.get("plain_english_explanation", "").strip():
        parsed["plain_english_explanation"] = (
            f"The system found {len(anomalies)} suspicious patterns in the network traffic. "
            f"This means some computers on the network were behaving in unusual ways "
            f"that could indicate an attack or security issue."
        )

    if not parsed.get("risk_impact", "").strip():
        parsed["risk_impact"] = (
            f"If the detected {risk.lower()}-risk activity is malicious, it could lead to "
            f"unauthorised access, data theft, or service disruption. "
            f"Immediate investigation of the flagged source IPs is recommended."
        )

    if not parsed.get("confidence_reasoning", "").strip():
        parsed["confidence_reasoning"] = (
            f"Confidence is based on {len(anomalies)} distinct anomaly signals "
            f"detected by multi-signal rules that require corroborating evidence "
            f"before firing. False positive risk is low due to minimum evidence filters."
        )

    if not parsed.get("likely_attack_types") or len(parsed["likely_attack_types"]) == 0:
        parsed["likely_attack_types"] = detected_types if detected_types else ["Unknown"]

    if not parsed.get("immediate_actions") or len(parsed["immediate_actions"]) == 0:
        parsed["immediate_actions"] = [
            "Review and investigate all flagged source IPs immediately.",
            "Check firewall logs for traffic from the anomalous source IPs.",
            "Capture additional packet data from suspicious hosts for forensic analysis.",
            "Alert the security team and begin incident response procedures.",
        ]

    if not parsed.get("long_term_prevention") or len(parsed["long_term_prevention"]) == 0:
        parsed["long_term_prevention"] = [
            "Deploy an IDS/IPS with rules matching the detected attack patterns.",
            "Implement network segmentation to limit lateral movement.",
            "Enable centralised logging and alerting for anomalous traffic volumes.",
            "Conduct regular network traffic baseline reviews.",
        ]

    return parsed


def _remap_to_frontend(parsed: dict) -> dict:
    """
    Remap AI model output fields to the frontend AIInsights interface.

    AI model returns:
        executive_summary, attack_story, technical_analysis,
        plain_english_explanation, immediate_actions, long_term_prevention

    Frontend expects:
        summary, explanation, recommended_actions, preventive_measures
    """
    summary_parts = [
        parsed.get("executive_summary", ""),
        parsed.get("attack_story", ""),
    ]
    summary = " ".join(p for p in summary_parts if p).strip() or "No summary available."

    explanation_parts = [
        parsed.get("technical_analysis", ""),
        parsed.get("plain_english_explanation", ""),
    ]
    explanation = " ".join(p for p in explanation_parts if p).strip() or "No explanation available."

    return {
        "summary":              summary,
        "risk_level":           parsed.get("risk_level", "Unknown"),
        "likely_attack_types":  parsed.get("likely_attack_types", ["Unknown"]),
        "explanation":          explanation,
        "recommended_actions":  parsed.get("immediate_actions", []) or ["Review detected anomalies manually."],
        "preventive_measures":  parsed.get("long_term_prevention", []) or ["Review security posture."],
        "ai_available":         parsed.get("ai_available", True),
    }


def _fallback_response(detected_types: List[str], reason: str) -> dict:
    risk = _infer_risk(detected_types)
    return {
        "summary":             f"AI analysis unavailable ({reason}). Rule-based risk: {risk}.",
        "risk_level":          risk,
        "likely_attack_types": list(dict.fromkeys(detected_types)) or ["Unknown"],
        "explanation": (
            "The AI insight layer could not complete analysis. "
            "Review the anomalies list for rule-based findings."
        ),
        "preventive_measures":  ["Review detected anomalies manually."],
        "recommended_actions":  ["Investigate flagged source IPs in your SIEM."],
        "ai_available":         False,
        "fallback_reason":      reason,
    }


# ── Ollama HTTP call ──────────────────────────────────────────────────────────

async def _call_ollama(
    client: httpx.AsyncClient,
    model:  str,
    prompt: str,
) -> str:
    last_exc: Optional[Exception] = None
    for attempt in range(1, AI_MAX_RETRIES + 1):
        try:
            r = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model":  model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,     # fully deterministic — same input = same output
                        "top_p":       1.0,   # must be 1.0 when temperature is 0
                        "seed":        42,    # fixed seed locks output across restarts
                        "num_predict": 2048,  # enough tokens for full structured response
                    },
                },
            )
            r.raise_for_status()
            return r.json()["response"]
        except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            last_exc = exc
            if attempt < AI_MAX_RETRIES:
                wait = 2 ** (attempt - 1)
                log.warning(
                    "Ollama call failed, retrying",
                    extra={"attempt": attempt, "model": model, "wait_s": wait},
                )
                await asyncio.sleep(wait)
    raise last_exc  # type: ignore[misc]


# ── Public entry point ────────────────────────────────────────────────────────

async def get_insights(data: dict) -> dict:
    anomalies      = data.get("anomalies", [])
    detected_types = [a.get("type", "") for a in anomalies if isinstance(a, dict)]

    anomalies_for_ai = sorted(
        [a for a in anomalies if isinstance(a, dict)],
        key=lambda x: _SEV_RANK_AI.get(x.get("severity", "Low"), 0),
        reverse=True,
    )[:AI_MAX_ANOMALIES]

    if len(anomalies) > AI_MAX_ANOMALIES:
        log.info(
            "AI prompt truncated",
            extra={"total": len(anomalies), "sent": len(anomalies_for_ai)},
        )

    prompt = build_analysis_prompt(
        summary               = data.get("summary", {}),
        anomalies_for_ai      = anomalies_for_ai,
        top_talkers           = data.get("top_talkers", []),
        protocol_distribution = data.get("protocol_distribution", {}),
        flows_sample          = data.get("flows", []),
    )

    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT_SECS) as client:
            raw    = await _call_ollama(client, AI_ANALYSIS_MODEL, prompt)
            parsed = _extract_json(raw)
            if parsed is None:
                log.warning("AI returned non-parseable JSON", extra={"raw_preview": raw[:300]})
                return _fallback_response(detected_types, "AI returned malformed JSON")

            parsed = _validate_ai_fields(parsed, detected_types)
            parsed = _fill_empty_fields(parsed, anomalies_for_ai, detected_types)
            parsed["ai_available"] = True
            return _remap_to_frontend(parsed)

    except asyncio.CancelledError:
        raise
    except httpx.TimeoutException:
        log.warning("AI layer timed out after retries")
        return _fallback_response(detected_types, "AI request timed out")
    except httpx.ConnectError:
        log.warning("Cannot reach Ollama", extra={"url": OLLAMA_BASE_URL})
        return _fallback_response(detected_types, "Ollama not reachable")
    except Exception as exc:
        log.error("AI insights error", extra={"error": str(exc)})
        return _fallback_response(detected_types, str(exc))
