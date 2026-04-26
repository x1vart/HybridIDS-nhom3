# ============================================================
# Module 2 - Run & Test Rule-Based Detection
# Chạy: python run_rule.py
# ============================================================

import json
import os
from datetime import datetime, timedelta
from rule_detector import RuleEngine


# ----------------------------------------------------------
# Generate data giả để test
# ----------------------------------------------------------

def gen_port_scan(src_ip, n=25):
    base = datetime(2026, 4, 3, 21, 0, 0)
    return [
        {
            "timestamp":   (base + timedelta(milliseconds=i*100)).isoformat(),
            "src_ip":      src_ip,
            "dst_ip":      "192.168.1.1",
            "src_port":    50000 + i,
            "dst_port":    1000 + i,
            "protocol":    "TCP",
            "packet_size": 60,
            "flags":       "SYN",
            "duration":    0.001
        }
        for i in range(n)
    ]


def gen_dos(src_ip, n=1100):
    base = datetime(2026, 4, 3, 21, 0, 0)
    return [
        {
            "timestamp":   (base + timedelta(milliseconds=i*0.5)).isoformat(),
            "src_ip":      src_ip,
            "dst_ip":      "192.168.1.1",
            "src_port":    12345,
            "dst_port":    80,
            "protocol":    "TCP",
            "packet_size": 512,
            "flags":       "SYN",
            "duration":    0.0005
        }
        for i in range(n)
    ]


def gen_brute_force(src_ip, n=15):
    base = datetime(2026, 4, 3, 21, 0, 0)
    return [
        {
            "timestamp":   (base + timedelta(seconds=i*0.5)).isoformat(),
            "src_ip":      src_ip,
            "dst_ip":      "192.168.1.1",
            "src_port":    60000 + i,
            "dst_port":    22,
            "protocol":    "TCP",
            "packet_size": 100,
            "flags":       "SYN",
            "duration":    0.001
        }
        for i in range(n)
    ]


def gen_normal(src_ip, n=10):
    base = datetime(2026, 4, 3, 21, 0, 0)
    return [
        {
            "timestamp":   (base + timedelta(seconds=i*5)).isoformat(),
            "src_ip":      src_ip,
            "dst_ip":      "192.168.1.1",
            "src_port":    50000 + i,
            "dst_port":    80,
            "protocol":    "TCP",
            "packet_size": 200,
            "flags":       "ACK",
            "duration":    0.1
        }
        for i in range(n)
    ]


# ----------------------------------------------------------
# Chạy test
# ----------------------------------------------------------

def run_test(name, packets, expect_alert):
    engine = RuleEngine()
    detected = False
    detail = ""

    for pkt in packets:
        result = engine.analyze(pkt)
        if result["alert"]:
            detected = True
            detail = result["alerts"][0]["detail"]
            attack_type = result["alerts"][0]["type"]
            break

    status = "PASS" if detected == expect_alert else "FAIL"
    if detected:
        print(f"[{status}] {name} → DETECTED: {attack_type} ({detail})")
    else:
        print(f"[{status}] {name} → No alert (expected={expect_alert})")
    return status == "PASS"


if __name__ == "__main__":
    print("=" * 55)
    print("  Module 2 - Rule-Based Detection Test")
    print("=" * 55)

    results = []
    results.append(run_test("Port Scan",      gen_port_scan("10.0.0.1"),    expect_alert=True))
    results.append(run_test("DoS Attack",     gen_dos("10.0.0.2"),          expect_alert=True))
    results.append(run_test("Brute Force",    gen_brute_force("10.0.0.3"),  expect_alert=True))
    results.append(run_test("Normal Traffic", gen_normal("10.0.0.4"),       expect_alert=False))

    print("=" * 55)
    print(f"  Kết quả: {sum(results)}/{len(results)} tests passed")
    print("=" * 55)

    # Lưu test data → dùng chung với các module khác
    os.makedirs("data", exist_ok=True)
    all_packets = (
        gen_port_scan("10.0.0.1") +
        gen_dos("10.0.0.2") +
        gen_brute_force("10.0.0.3") +
        gen_normal("10.0.0.4")
    )
    with open("data/test_packets.json", "w", encoding="utf-8") as f:
        json.dump(all_packets, f, indent=2, ensure_ascii=False)
    print("\n  Test data → data/test_packets.json")