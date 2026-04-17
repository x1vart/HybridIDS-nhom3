from pathlib import Path
import sys
import argparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from capture import capture_packet, list_capture_interfaces


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Data Capture module")
    parser.add_argument(
        "--mode",
        choices=["mock", "live"],
        default="mock",
        help="Capture mode: mock (default) or live",
    )
    parser.add_argument(
        "--iface",
        default=None,
        help="Network interface for live mode (optional)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Sniff timeout in seconds for live mode",
    )
    parser.add_argument(
        "--filter",
        dest="packet_filter",
        default=None,
        help='BPF filter for live mode, e.g. "tcp" or "udp"',
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="How many packets to sniff in live mode (default: 1)",
    )
    parser.add_argument(
        "--list-ifaces",
        action="store_true",
        help="List available capture interfaces then exit",
    )
    args = parser.parse_args()

    if args.list_ifaces:
        for iface_name in list_capture_interfaces():
            print(iface_name)
        raise SystemExit(0)

    try:
        packet = capture_packet(
            mode=args.mode,
            iface=args.iface,
            timeout=args.timeout,
            packet_filter=args.packet_filter,
            count=args.count,
        )
    except Exception as exc:
        print(f"[capture] ERROR: {exc}")
        raise SystemExit(1)

    print(packet)
