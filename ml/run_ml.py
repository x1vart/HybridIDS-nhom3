from pathlib import Path
import sys
import argparse
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml import predict
from shared.utils import load_json


def _load_features(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unsupported JSON format in {input_path}. Expected dict or list of dict.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ML detector with mock features or converted CICIDS JSON features."
    )
    parser.add_argument(
        "--input",
        default="shared/mock/mock_features.json",
        help="Path to input JSON. Supports a single feature dict or list of feature dicts.",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="If input JSON is a list, choose which item to run.",
    )
    args = parser.parse_args()

    if args.input.endswith(".json"):
        if args.input == "shared/mock/mock_features.json":
            features = load_json(args.input)
        else:
            rows = _load_features(args.input)
            if not rows:
                raise ValueError(f"No feature rows found in {args.input}")
            if args.index < 0 or args.index >= len(rows):
                raise IndexError(
                    f"--index out of range. Got {args.index}, but input has {len(rows)} rows."
                )
            features = rows[args.index]
            print(f"[run_ml] Loaded {len(rows)} rows from {args.input}; using index {args.index}")
    else:
        raise ValueError("Only JSON input is currently supported.")

    result = predict(features)
    print(result)
