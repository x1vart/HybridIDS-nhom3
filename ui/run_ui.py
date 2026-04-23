"""
ui/run_ui.py
============
Run UI module independently with mock data.
Contract: "Có thể chạy với mock data bằng python ui/run_ui.py"

Usage:
    python ui/run_ui.py                    # Generate diverse mock test data
    python ui/run_ui.py --scenario dos     # Generate one scenario
    python ui/run_ui.py --app              # Launch Streamlit dashboard
"""

import argparse
import copy
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ui import show
from shared.utils import load_json, get_mock_path


BASE_RULE_FILE = "mock_rule_alert.json"
BASE_ML_FILE = "mock_ml_result.json"


def _clear_test_log() -> None:
    test_log_path = ROOT_DIR / "shared" / "output" / "alert_log_test.jsonl"
    if test_log_path.exists():
        test_log_path.unlink()


def _strip_internal_keys(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key != "__cases__"}


def _load_test_cases() -> tuple[dict, dict, dict]:
    """Load base payloads and scenarios embedded in base mock files."""
    rule_base = load_json(get_mock_path(BASE_RULE_FILE))
    ml_base = load_json(get_mock_path(BASE_ML_FILE))

    rule_cases = rule_base.get("__cases__", {}) if isinstance(rule_base, dict) else {}
    ml_cases = ml_base.get("__cases__", {}) if isinstance(ml_base, dict) else {}

    scenario_names = sorted(set(rule_cases.keys()) & set(ml_cases.keys()))
    cases = {name: {"rule": rule_cases[name], "ml": ml_cases[name]} for name in scenario_names}
    return _strip_internal_keys(rule_base), _strip_internal_keys(ml_base), cases


def _build_scenario_payload(
    scenario: str,
    rule_base: dict,
    ml_base: dict,
    test_cases: dict,
) -> tuple[dict, dict]:
    """Return rule/ml payloads for a named scenario using the base mock files."""
    if scenario not in test_cases:
        raise ValueError(
            f"Unknown scenario '{scenario}'. Available: {', '.join(test_cases.keys())}"
        )

    rule_data = copy.deepcopy(rule_base)
    ml_data = copy.deepcopy(ml_base)

    rule_overrides = test_cases[scenario]["rule"]
    ml_overrides = test_cases[scenario]["ml"]
    rule_data.update(rule_overrides)
    ml_data.update(ml_overrides)
    return rule_data, ml_data


def run_mock(scenario: str = "all"):
    """Load mock data and call show() with test=True."""
    rule_base, ml_base, test_cases = _load_test_cases()

    if not test_cases:
        raise ValueError("No test scenarios found. Add '__cases__' to both mock_rule_alert.json and mock_ml_result.json")

    if scenario == "all":
        _clear_test_log()
        for scenario_name in test_cases:
            rule_data, ml_data = _build_scenario_payload(
                scenario_name,
                rule_base,
                ml_base,
                test_cases,
            )
            show(rule_data, ml_data, test=True)
            print(f"✅ run_ui: scenario '{scenario_name}' written to alert_log_test.jsonl")
        print("✅ run_ui: diverse mock data processed successfully (alert_log_test.jsonl).")
        return

    rule_data, ml_data = _build_scenario_payload(scenario, rule_base, ml_base, test_cases)
    show(rule_data, ml_data, test=True)
    print(f"✅ run_ui: scenario '{scenario}' processed successfully (alert_log_test.jsonl).")


def run_app():
    """Launch Streamlit dashboard as a separate process."""
    import subprocess
    print("Khởi động Hybrid IDS Dashboard...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(ROOT_DIR / "ui" / "app.py")],
        cwd=str(ROOT_DIR),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UI with mock data or launch dashboard.")
    parser.add_argument("--app", action="store_true", help="Launch Streamlit dashboard")
    parser.add_argument(
        "--scenario",
        default="all",
        help="Mock data scenario to write into alert_log_test.jsonl",
    )
    args = parser.parse_args()

    if args.app:
        run_app()
    else:
        run_mock(args.scenario)
