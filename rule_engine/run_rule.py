from pathlib import Path
import sys
import argparse
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rule_engine import detect
from shared.utils import load_json


def _load_packets(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unsupported JSON format in {input_path}. Expected dict or list of dict.")


def _extract_base_and_cases(payload: dict):
    base_packet = {k: v for k, v in payload.items() if k != "__cases__"}
    cases = payload.get("__cases__", {})
    if not isinstance(cases, dict):
        cases = {}
    return base_packet, cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Rule detector with mock packet data (single dict or list of dicts)."
    )
    parser.add_argument(
        "--input",
        default="shared/mock/mock_packet.json",
        help="Path to input JSON. Supports a single packet dict or list of packet dicts.",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="If input JSON is a list, choose which item to run.",
    )
    parser.add_argument(
        "--scenario",
        default="default",
        help="Scenario name from '__cases__' when input JSON is a dict. Use 'all' to run all scenarios.",
    )
    args = parser.parse_args()

    if args.input == "shared/mock/mock_packet.json":
        payload = load_json(args.input)
        if isinstance(payload, dict):
            base_packet, cases = _extract_base_and_cases(payload)

            if args.scenario == "default":
                packet = base_packet
            elif args.scenario == "all":
                if not cases:
                    raise ValueError("No '__cases__' found in mock_packet.json")
                for scenario_name, overrides in cases.items():
                    scenario_packet = dict(base_packet)
                    scenario_packet.update(overrides)
                    result = detect(scenario_packet)
                    print(f"[run_rule] scenario={scenario_name}")
                    print(result)
                raise SystemExit(0)
            else:
                if args.scenario not in cases:
                    raise ValueError(
                        f"Unknown scenario '{args.scenario}'. Available: default, all, {', '.join(cases.keys())}"
                    )
                packet = dict(base_packet)
                packet.update(cases[args.scenario])
        else:
            packet = payload
    else:
        rows = _load_packets(args.input)
        if not rows:
            raise ValueError(f"No packet rows found in {args.input}")
        if args.index < 0 or args.index >= len(rows):
            raise IndexError(f"--index out of range. Got {args.index}, but input has {len(rows)} rows.")
        packet = rows[args.index]
        print(f"[run_rule] Loaded {len(rows)} rows from {args.input}; using index {args.index}")

    result = detect(packet)
    print(result)
