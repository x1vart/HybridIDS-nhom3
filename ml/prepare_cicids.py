from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.utils import now_iso


def _pick(row: pd.Series, candidates: list[str], default=None):
    for col in candidates:
        if col in row and pd.notna(row[col]):
            return row[col]
    return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _protocol_name(value) -> str:
    if isinstance(value, str):
        v = value.strip().upper()
        if v:
            return v
    code = _to_int(value, default=-1)
    mapping = {1: "ICMP", 6: "TCP", 17: "UDP"}
    return mapping.get(code, "TCP")


def _flags_from_row(row: pd.Series) -> str:
    checks = [
        ("SYN Flag Count", "SYN"),
        ("ACK Flag Count", "ACK"),
        ("FIN Flag Count", "FIN"),
        ("RST Flag Count", "RST"),
        ("PSH Flag Count", "PSH"),
        ("URG Flag Count", "URG"),
    ]
    for col, name in checks:
        if col in row and _to_int(row[col], 0) > 0:
            return name
    return "NONE"


def _packet_count(row: pd.Series) -> int:
    total = _to_float(_pick(row, ["Total Fwd Packets", "Tot Fwd Pkts"], 0), 0.0) + _to_float(
        _pick(row, ["Total Backward Packets", "Tot Bwd Pkts"], 0), 0.0
    )
    if total > 0:
        return int(total)
    fallback = _pick(row, ["Packet Count", "Total Packets"], 1)
    return max(1, _to_int(fallback, 1))


def _duration_seconds(row: pd.Series) -> float:
    raw = _to_float(_pick(row, ["Flow Duration", "Duration"], 0.0), 0.0)
    # CICIDS2017 Flow Duration is usually in microseconds.
    if raw > 1000:
        return raw / 1_000_000.0
    return raw


def convert_row(row: pd.Series) -> dict:
    src_ip = str(_pick(row, ["Source IP", "Src IP"], "0.0.0.0"))
    dst_ip = str(_pick(row, ["Destination IP", "Dst IP"], "0.0.0.0"))
    dst_port = _to_int(_pick(row, ["Destination Port", "Dst Port"], 0), 0)
    protocol = _protocol_name(_pick(row, ["Protocol"], 6))
    packet_count = _packet_count(row)
    connection_duration = _duration_seconds(row)
    avg_packet_size = _to_float(
        _pick(row, ["Average Packet Size", "Packet Length Mean", "Avg Packet Size"], 0.0),
        0.0,
    )
    flags = _flags_from_row(row)
    timestamp = str(_pick(row, ["Timestamp", "timestamp"], now_iso()))

    return {
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "dst_port": dst_port,
        "protocol": protocol,
        "packet_count": packet_count,
        "connection_duration": connection_duration,
        "avg_packet_size": avg_packet_size,
        "flags": flags,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert CICIDS2017 CSV rows to project FeatureVector JSON format."
    )
    parser.add_argument("--csv", required=True, help="Path to CICIDS2017 CSV file")
    parser.add_argument(
        "--output",
        default="shared/mock/cicids_features.json",
        help="Output JSON path (list of feature dicts)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=200,
        help="Maximum number of rows to convert",
    )
    parser.add_argument(
        "--replace-mock",
        action="store_true",
        help="Also overwrite shared/mock/mock_features.json with the first converted row",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    if df.empty:
        raise ValueError(f"CSV has no rows: {args.csv}")

    rows = [convert_row(r) for _, r in df.head(max(1, args.max_rows)).iterrows()]

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"[prepare_cicids] Wrote {len(rows)} rows to {out_path}")

    if args.replace_mock and rows:
        mock_path = ROOT_DIR / "shared" / "mock" / "mock_features.json"
        with open(mock_path, "w", encoding="utf-8") as f:
            json.dump(rows[0], f, indent=2)
        print(f"[prepare_cicids] Updated {mock_path} with first converted row")


if __name__ == "__main__":
    main()
