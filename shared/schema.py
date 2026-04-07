"""
================
Định nghĩa schema dữ liệu chung cho toàn bộ hệ thống IDS.
Tất cả module PHẢI import từ file này — không tự định nghĩa lại.

# Ví dụ người làm Rule-based:
from shared.schema import FeatureVector, RuleAlert
from shared.utils import load_json

data = load_json("shared/mock/mock_features.json")
features = FeatureVector(**data)

# ... logic của mình

"""

from dataclasses import dataclass, field, asdict

try:
    from .utils import now_iso, to_json
except ImportError:
    # Allow running "python shared/schema.py" directly.
    from utils import now_iso, to_json


# ──────────────────────────────────────────────
# Schema 1: PacketEvent
# Module: Data Capture → output
# ──────────────────────────────────────────────

@dataclass
class PacketEvent:
    """
    Dữ liệu packet thô sau khi capture từ mạng.
    Output của module Data Capture.
    """
    src_ip: str                          # IP nguồn
    dst_ip: str                          # IP đích
    src_port: int                        # Port nguồn
    dst_port: int                        # Port đích
    protocol: str                        # TCP | UDP | ICMP
    packet_size: int                     # Kích thước packet (bytes)
    flags: str                           # TCP flags: SYN, ACK, FIN, RST, ...
    duration: float                      # Thời gian giữa các packet (giây)
    timestamp: str = field(default_factory=now_iso)  # Tự động gán nếu không truyền

    def validate(self) -> bool:
        """Kiểm tra dữ liệu hợp lệ trước khi truyền sang module khác."""
        assert self.protocol in ("TCP", "UDP", "ICMP"), f"Protocol không hợp lệ: {self.protocol}"
        assert 0 <= self.src_port <= 65535, "src_port ngoài range"
        assert 0 <= self.dst_port <= 65535, "dst_port ngoài range"
        assert self.packet_size >= 0, "packet_size không được âm"
        return True

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return to_json(self)


# ──────────────────────────────────────────────
# Schema 2: FeatureVector
# Module: Feature Extraction → output (input cho Rule + ML)
# ──────────────────────────────────────────────

@dataclass
class FeatureVector:
    """
    Feature đã được trích xuất, dùng làm input cho Rule-based và ML.
    """
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    packet_count: int                    # Số packet trong cùng 1 luồng
    connection_duration: float           # Tổng thời gian kết nối (giây)
    avg_packet_size: float               # Kích thước packet trung bình
    flags: str
    timestamp: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return to_json(self)


# ──────────────────────────────────────────────
# Schema 3: RuleAlert
# Module: Rule-based Detection → output
# ──────────────────────────────────────────────

VALID_ATTACK_TYPES = ("Port Scan", "Brute Force", "DoS", "None")

@dataclass
class RuleAlert:
    """
    Kết quả phát hiện từ Rule-based engine.
    alert=False nếu không có gì bất thường.
    """
    alert: bool
    type: str                            # Port Scan | Brute Force | DoS | None
    src_ip: str
    dst_ip: str
    dst_port: int
    reason: str                          # Mô tả lý do bị flag
    timestamp: str = field(default_factory=now_iso)

    def validate(self) -> bool:
        assert self.type in VALID_ATTACK_TYPES, f"Attack type không hợp lệ: {self.type}"
        if not self.alert:
            assert self.type == "None", "Nếu alert=False thì type phải là 'None'"
        return True

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return to_json(self)


# ──────────────────────────────────────────────
# Schema 4: MLResult
# Module: Machine Learning → output
# ──────────────────────────────────────────────

VALID_PREDICTIONS = ("Normal", "DoS", "Port Scan", "Brute Force", "Unknown")

@dataclass
class MLResult:
    """
    Kết quả phân loại từ ML model.
    """
    prediction: str                      # Normal | DoS | Port Scan | Brute Force | Unknown
    confidence: float                    # 0.0 – 1.0
    src_ip: str
    timestamp: str = field(default_factory=now_iso)

    def validate(self) -> bool:
        assert self.prediction in VALID_PREDICTIONS, f"Prediction không hợp lệ: {self.prediction}"
        assert 0.0 <= self.confidence <= 1.0, "Confidence phải trong khoảng [0, 1]"
        return True

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return to_json(self)


# ──────────────────────────────────────────────
# Schema 5: AlertLog
# Module: Alert & Logging → output (input cho UI)
# ──────────────────────────────────────────────

@dataclass
class AlertLog:
    """
    Bản ghi cảnh báo cuối cùng — tổng hợp từ Rule + ML.
    Đây là dữ liệu mà UI đọc để hiển thị.
    """
    attack_type: str                     # Loại tấn công (ưu tiên Rule nếu có)
    source_ip: str
    destination_ip: str
    confidence: float                    # Từ ML result
    rule_triggered: bool                 # Rule-based có kích hoạt không
    ml_prediction: str                   # Raw prediction từ ML
    severity: str                        # low | medium | high
    timestamp: str = field(default_factory=now_iso)

    def validate(self) -> bool:
        assert self.severity in ("low", "medium", "high"), f"Severity không hợp lệ: {self.severity}"
        return True

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return to_json(self)


# ──────────────────────────────────────────────
# Factory: tạo AlertLog từ RuleAlert + MLResult
# Nhóm trưởng dùng trong main.py
# ──────────────────────────────────────────────

def build_alert_log(rule: RuleAlert, ml: MLResult) -> AlertLog:
    """
    Kết hợp kết quả Rule-based và ML thành AlertLog.
    Logic ưu tiên:
      - Nếu rule triggered → dùng rule type làm attack_type
      - Nếu rule không triggered → dùng ML prediction
      - Severity dựa trên confidence + rule
    """
    if rule.alert:
        attack_type = rule.type
    elif ml.prediction != "Normal" and ml.prediction != "Unknown":
        attack_type = ml.prediction
    else:
        attack_type = "None"

    # Xác định severity
    if rule.alert and ml.confidence >= 0.85:
        severity = "high"
    elif rule.alert or ml.confidence >= 0.60:
        severity = "medium"
    else:
        severity = "low"

    return AlertLog(
        attack_type=attack_type,
        source_ip=rule.src_ip,
        destination_ip=rule.dst_ip,
        confidence=ml.confidence,
        rule_triggered=rule.alert,
        ml_prediction=ml.prediction,
        severity=severity,
    )


# ──────────────────────────────────────────────
# Quick test — chạy trực tiếp file này để verify
# python shared/schema.py
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Kiểm tra Schema ===\n")

    packet = PacketEvent(
        src_ip="192.168.1.10", dst_ip="192.168.1.1",
        src_port=54321, dst_port=80,
        protocol="TCP", packet_size=512,
        flags="SYN", duration=0.002
    )
    packet.validate()
    print("✅ PacketEvent OK")
    print(packet.to_json(), "\n")

    features = FeatureVector(
        src_ip="192.168.1.10", dst_ip="192.168.1.1",
        dst_port=80, protocol="TCP",
        packet_count=15, connection_duration=2.5,
        avg_packet_size=480.0, flags="SYN"
    )
    print("✅ FeatureVector OK")

    rule = RuleAlert(
        alert=True, type="Port Scan",
        src_ip="192.168.1.10", dst_ip="192.168.1.1",
        dst_port=80, reason="SYN scan trên nhiều port trong 1 giây"
    )
    rule.validate()
    print("✅ RuleAlert OK")

    ml = MLResult(
        prediction="Port Scan", confidence=0.91,
        src_ip="192.168.1.10"
    )
    ml.validate()
    print("✅ MLResult OK")

    log = build_alert_log(rule, ml)
    log.validate()
    print("✅ AlertLog OK")
    print(log.to_json())
