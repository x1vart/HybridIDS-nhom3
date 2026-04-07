from capture import capture_packet
from rule_engine import detect
from ml import predict
from ui import show


def main():
	packet = capture_packet()
	rule = detect(packet)
	ml = predict(packet)
	show(rule, ml)
	print("Done")


if __name__ == "__main__":
	main()