from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ui import show
from shared.utils import load_json


if __name__ == "__main__":
    alert = load_json("shared/mock/mock_rule_alert.json")
    show(alert)
