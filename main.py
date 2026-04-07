from capture import capture_packet
from rule_engine import detect_rule
from ML import detect_ml

packet = capture_packet()
rule = detect_rule(packet)
ml = detect_ml(packet)

print("Done")