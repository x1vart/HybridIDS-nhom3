"""
ui/run_ui.py
============
Run UI module independently with mock data.
Contract: "Có thể chạy với mock data bằng python ui/run_ui.py"

Usage:
    python ui/run_ui.py          # Test show() with mock data (writes to alert_log.jsonl)
    python ui/run_ui.py --app    # Launch Streamlit dashboard
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ui import show
from shared.utils import load_json, get_mock_path


def run_mock():
    """Load mock rule_alert + mock ml_result and call show()."""
    rule_data = load_json(get_mock_path("mock_rule_alert.json"))
    ml_data = load_json(get_mock_path("mock_ml_result.json"))
    show(rule_data, ml_data)
    print("✅ run_ui: mock data processed successfully.")


def run_app():
    """Launch Streamlit dashboard as a separate process."""
    import subprocess
    print("Khởi động Hybrid IDS Dashboard...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(ROOT_DIR / "ui" / "app.py")],
        cwd=str(ROOT_DIR),
    )


if __name__ == "__main__":
    if "--app" in sys.argv:
        run_app()
    else:
        run_mock()
