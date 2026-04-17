import argparse

from capture import capture_packet
from rule_engine import detect
from ml import predict
from ui import show


def main():
	parser = argparse.ArgumentParser(description="Run HybridIDS pipeline")
	parser.add_argument("--mode", choices=["mock", "live"], default="mock")
	parser.add_argument("--iface", default=None)
	parser.add_argument("--timeout", type=int, default=10)
	parser.add_argument("--filter", dest="packet_filter", default=None)
	parser.add_argument("--count", type=int, default=1)
	parser.add_argument(
		"--batch",
		action="store_true",
		help="Capture/analyze all packets in one sniff window instead of only the last one",
	)
	args = parser.parse_args()

	capture_payload = capture_packet(
		mode=args.mode,
		iface=args.iface,
		timeout=args.timeout,
		packet_filter=args.packet_filter,
		count=args.count,
		return_batch=args.batch,
	)

	if isinstance(capture_payload, list):
		analysis_payload = capture_payload[-1]
	else:
		analysis_payload = capture_payload

	rule = detect(analysis_payload)
	ml = predict(analysis_payload)
	show(rule, ml)

	if isinstance(capture_payload, list):
		print(f"Done (processed {len(capture_payload)} captured events)")
	else:
		print("Done (processed 1 captured event)")


if __name__ == "__main__":
	main()