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
import warnings
from pathlib import Path

from shared.schema import build_alert_log, RuleAlert, MLResult

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "shared", "output",
)
LOG_FILE = os.path.join(OUTPUT_DIR, "alert_log.jsonl")
TEST_LOG_FILE = os.path.join(OUTPUT_DIR, "alert_log_test.jsonl")
MAX_LOG_SIZE_MB = 10  # Rotate when log exceeds 10MB


def _rotate_log_if_needed() -> None:
    """Rotate log file if it exceeds MAX_LOG_SIZE_MB."""
    if not os.path.exists(LOG_FILE):
        return
    
    file_size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
    if file_size_mb > MAX_LOG_SIZE_MB:
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        archive = f"{LOG_FILE}.{timestamp}.bak"
        os.rename(LOG_FILE, archive)
        print(f"[LOG ROTATION] Rotated to {archive}")


def _warn_fallback(kind: str, reason: str) -> None:
    warnings.warn(
        f"[ui.dashboard] {kind} fallback used: {reason}",
        RuntimeWarning,
        stacklevel=3,
    )


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
    _warn_fallback("RuleAlert", "missing or empty input payload")
    return RuleAlert(
        alert=False,
        type="None",
        src_ip="0.0.0.0",
        dst_ip="0.0.0.0",
        dst_port=0,
        reason="Fallback RuleAlert created because upstream data was missing.",
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
    _warn_fallback("MLResult", "missing or empty input payload")
    return MLResult(
        prediction="Unknown",
        confidence=0.0,
        src_ip=fallback_ip,
    )


def show(rule_result, ml_result=None, test=False):
    """
    Receive detection results, build AlertLog, and append to log file.

    Parameters
    ----------
    rule_result : dict | RuleAlert
        Output from Rule-based detection module.
    ml_result : dict | MLResult | None
        Output from ML detection module.
    test : bool
        If True, write to alert_log_test.jsonl (mock test file).
        If False, write to alert_log.jsonl (production file).
    """
    rule = _to_rule_alert(rule_result)
    ml = _to_ml_result(ml_result, fallback_ip=rule.src_ip)

    alert_log = build_alert_log(rule, ml)
    alert_log.validate()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    log_path = TEST_LOG_FILE if test else LOG_FILE
    if not test:
        _rotate_log_if_needed()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(alert_log.to_dict(), ensure_ascii=False) + "\n")

    # Console feedback
    log_name = os.path.basename(log_path)
    if alert_log.severity == "high":
        print(f"[HIGH ALERT] {alert_log.attack_type} from {alert_log.source_ip}")
    else:
        print(f"[LOG] Saved {alert_log.attack_type} to {log_name}")


def show_alert(alert):
    """Backward-compatible alias."""
    return show(alert)