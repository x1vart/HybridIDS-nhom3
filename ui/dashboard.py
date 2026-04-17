"""
ui/dashboard.py
===============
Core integration module for UI.
Entry point: show(rule_result, ml_result)

Receives detection results from the pipeline (main.py),
builds an AlertLog via shared.schema, and appends it to
shared/output/alert_log.jsonl for the Streamlit dashboard.
"""

import json
import os
import random

from shared.schema import build_alert_log, RuleAlert, MLResult

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "shared", "output",
)
LOG_FILE = os.path.join(OUTPUT_DIR, "alert_log.jsonl")


def _to_rule_alert(data) -> RuleAlert:
    """Convert a dict or RuleAlert into a validated RuleAlert."""
    if isinstance(data, RuleAlert):
        return data
    if isinstance(data, dict) and data:
        return RuleAlert(
            alert=data.get("alert", False),
            type=data.get("type", "None"),
            src_ip=data.get("src_ip", "0.0.0.0"),
            dst_ip=data.get("dst_ip", "0.0.0.0"),
            dst_port=data.get("dst_port", 0),
            reason=data.get("reason", ""),
        )
    # Fallback: generate random mock data when upstream is a stub ({})
    is_alert = random.choice([True, False, False])
    return RuleAlert(
        alert=is_alert,
        type=random.choice(["Port Scan", "DoS", "Brute Force"]) if is_alert else "None",
        src_ip=f"192.168.1.{random.randint(2, 20)}",
        dst_ip="192.168.1.1",
        dst_port=80,
        reason="Auto-generated mock rule",
    )


def _to_ml_result(data, fallback_ip: str = "0.0.0.0") -> MLResult:
    """Convert a dict or MLResult into a validated MLResult."""
    if isinstance(data, MLResult):
        return data
    if isinstance(data, dict) and data:
        return MLResult(
            prediction=data.get("prediction", "Unknown"),
            confidence=data.get("confidence", 0.0),
            src_ip=data.get("src_ip", fallback_ip),
        )
    # Fallback: generate random mock data when upstream is a stub ({})
    return MLResult(
        prediction=random.choice(["Normal", "DoS", "Port Scan", "Brute Force", "Unknown"]),
        confidence=round(random.uniform(0.50, 0.99), 4),
        src_ip=fallback_ip,
    )


def show(rule_result, ml_result=None):
    """
    Receive detection results, build AlertLog, and append to log file.

    Parameters
    ----------
    rule_result : dict | RuleAlert
        Output from Rule-based detection module.
    ml_result : dict | MLResult | None
        Output from ML detection module.
    """
    rule = _to_rule_alert(rule_result)
    ml = _to_ml_result(ml_result, fallback_ip=rule.src_ip)

    alert_log = build_alert_log(rule, ml)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(alert_log.to_dict(), ensure_ascii=False) + "\n")

    # Console feedback
    if alert_log.severity == "high":
        print(f"[HIGH ALERT] {alert_log.attack_type} from {alert_log.source_ip}")
    else:
        print(f"[LOG] Saved {alert_log.attack_type} to alert_log.jsonl")


def show_alert(alert):
    """Backward-compatible alias."""
    return show(alert)