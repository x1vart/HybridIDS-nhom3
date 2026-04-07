from capture.capture import capture_packet
from rule_engine.rule_detector import detect_rule
from ML.ml_detector import detect_ml

packet = capture_packet()
rule = detect_rule(packet)
ml = detect_ml(packet)

print("Done")