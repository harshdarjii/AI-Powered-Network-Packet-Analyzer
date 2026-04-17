"""
DeepTrace — AI Prompt Builder
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


def build_analysis_prompt(
    summary:               Dict[str, Any],
    anomalies_for_ai:      List[dict],
    top_talkers:           List[dict],
    protocol_distribution: Dict[str, int],
    flows_sample:          List[dict],
) -> str:

    anomaly_count  = len(anomalies_for_ai)
    severities     = [a.get("severity", "Low") for a in anomalies_for_ai]
    types_detected = list(dict.fromkeys(a.get("type", "") for a in anomalies_for_ai))

    return f"""You are a senior cybersecurity analyst writing a formal incident report.

You have been given network traffic analysis results from the DeepTrace engine.
Your task is to write a precise, professional forensic analysis based ONLY on the data provided.

=== DETECTION RESULTS ===

CAPTURE SUMMARY:
{json.dumps(summary, indent=2)}

ANOMALIES DETECTED ({anomaly_count} total):
{json.dumps(anomalies_for_ai, indent=2)}

TOP TALKERS (highest traffic sources):
{json.dumps(top_talkers, indent=2)}

PROTOCOL DISTRIBUTION:
{json.dumps(protocol_distribution, indent=2)}

FLOW SAMPLE (first 30 flows):
{json.dumps(flows_sample[:30], indent=2)}

=== YOUR TASK ===

Write a complete forensic analysis. Fill every field with real content based on the data above.
Do not leave any field empty. Do not use placeholder text.

Field-by-field instructions:

"executive_summary":
  Write 2-3 sentences. State what was detected, which source IPs are suspicious,
  and the overall severity. Example format: "Analysis of [X] flows over [duration]
  identified [N] anomalies from [IP list]. The most severe finding is [type] from [IP].
  Overall risk is assessed as [level]."

"attack_story":
  Write a narrative of what the attacker likely did step by step.
  Reference the actual anomaly types detected: {types_detected}.
  Example: "The source IP X.X.X.X began with a port scan across Y ports,
  followed by brute force attempts on SSH, suggesting a reconnaissance
  phase leading to credential attack."

"technical_analysis":
  For each anomaly type detected, explain the technical significance.
  Reference actual IPs, port counts, packet counts from the data.
  Be specific — use numbers from the anomaly descriptions.

"plain_english_explanation":
  Explain what happened in simple terms a non-technical person can understand.
  No jargon. Use analogies if helpful.
  Example: "Someone was trying every door in a building to see which ones
  were unlocked, then attempting to guess the password on the ones they found."

"risk_level":
  Must be exactly one of: "Low", "Medium", "High", "Critical"
  Base this on the severities detected: {severities}

"risk_impact":
  What damage could result if this attack succeeded?
  Be specific to the attack types found.

"confidence_reasoning":
  Explain how confident you are in this analysis and why.
  Reference the volume of evidence — number of flows, number of anomalies,
  consistency of patterns.

"likely_attack_types":
  List of strings naming the attack categories observed.
  Use the detected types as your basis: {types_detected}
  Each entry should be a short label like "Port Scan", "Brute Force", "DNS Tunneling" etc.

"immediate_actions":
  List of 3-5 specific actions the security team should take RIGHT NOW.
  Example actions: "Block IP X.X.X.X at the firewall", "Review SSH logs for successful logins",
  "Capture full packet data from [IP] for forensic analysis"
  Reference actual IPs and ports from the data.

"long_term_prevention":
  List of 3-5 strategic security improvements to prevent this in future.
  Examples: "Implement fail2ban for SSH brute force protection",
  "Deploy network segmentation to limit lateral movement",
  "Enable DNS query logging and alerting for anomalous volumes"

=== STRICT RULES ===
- Output ONLY valid JSON. No text before or after the JSON.
- Do NOT invent CVE numbers or specific software vulnerabilities.
- Do NOT use placeholder text like "Insert analysis here".
- Every string field must contain at least 2 sentences of real content.
- Every list field must contain at least 3 items.
- Base everything on the actual data provided above.

OUTPUT FORMAT (fill every value — no empty strings or empty lists):

{{
  "executive_summary": "...",
  "attack_story": "...",
  "technical_analysis": "...",
  "plain_english_explanation": "...",
  "risk_level": "Low|Medium|High|Critical",
  "risk_impact": "...",
  "confidence_reasoning": "...",
  "likely_attack_types": ["...", "...", "..."],
  "immediate_actions": ["...", "...", "...", "..."],
  "long_term_prevention": ["...", "...", "...", "..."]
}}"""