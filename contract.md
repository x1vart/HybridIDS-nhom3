# IDS Project — Module Contract

> **Tài liệu này là chuẩn giao tiếp bắt buộc giữa các module.**
> Mọi thay đổi về field/format phải được nhóm trưởng duyệt trước khi áp dụng.

---

## 1. Tổng quan pipeline

```
[Network]
   │
   ▼
[Data Capture]  ──── packet_event.json ────►  [Feature Extraction]
                                                       │
                                          feature_vector.json
                                                       │
                                        ┌──────────────┴──────────────┐
                                        ▼                             ▼
                               [Rule-based Detection]        [ML Detection]
                                        │                             │
                               rule_alert.json               ml_result.json
                                        └──────────────┬──────────────┘
                                                       ▼
                                              [Alert & Logging]
                                                       │
                                              alert_log.json
                                                       │
                                                       ▼
                                                    [UI]
```

---

## 2. Phân công và dữ liệu từng module

### 2.1 Data Capture — Thành viên 1

| | |
|---|---|
| **Input** | Raw packet từ network (Scapy/PyShark) |
| **Output** | `packet_event.json` |
| **Mock file** | `shared/mock/mock_packet.json` |

**Output schema:**
```json
{
  "timestamp": "ISO 8601",
  "src_ip": "string",
  "dst_ip": "string",
  "src_port": "int",
  "dst_port": "int",
  "protocol": "TCP | UDP | ICMP",
  "packet_size": "int (bytes)",
  "flags": "string (SYN, ACK, FIN, ...)",
  "duration": "float (seconds)"
}
```

**Yêu cầu:**
- Hàm entry point: `capture.capture_packet() → dict`
- Có thể chạy độc lập bằng `python capture/run_capture.py`
- Ghi output ra `shared/output/packet_event.json`

---

### 2.2 Rule-based Detection — Thành viên 2

| | |
|---|---|
| **Input** | `feature_vector.json` (hoặc trực tiếp `packet_event.json`) |
| **Output** | `rule_alert.json` |
| **Mock file** | `shared/mock/mock_features.json` |

**Output schema:**
```json
{
  "alert": "bool",
  "type": "Port Scan | Brute Force | DoS | None",
  "src_ip": "string",
  "dst_ip": "string",
  "dst_port": "int",
  "reason": "string (mô tả tại sao bị flag)"
}
```

**Yêu cầu:**
- Hàm entry point: `rule_engine.rule_detector.detect(features: dict) → dict`
- Có thể chạy độc lập bằng `python rule_engine/run_rule.py`
- Trả về `alert: false` nếu không phát hiện gì (không raise exception)

---

### 2.3 Machine Learning — Thành viên 3

| | |
|---|---|
| **Input** | `feature_vector.json` |
| **Output** | `ml_result.json` |
| **Mock file** | `shared/mock/mock_features.json` |

**Output schema:**
```json
{
  "prediction": "Normal | DoS | Port Scan | Brute Force",
  "confidence": "float (0.0 – 1.0)",
  "src_ip": "string",
  "timestamp": "ISO 8601"
}
```

**Yêu cầu:**
- Hàm entry point: `ml.ml_detector.predict(features: dict) → dict`
- Model được lưu tại `ml/model/ids_model.pkl`
- Có thể chạy độc lập bằng `python ml/run_ml.py`
- Nếu model chưa train, trả về `prediction: "Unknown"`, `confidence: 0.0`

---

### 2.4 UI + Integration — Thành viên 4 (+ Nhóm trưởng)

| | |
|---|---|
| **Input** | `rule_alert.json` + `ml_result.json` |
| **Output** | Dashboard hiển thị real-time |
| **Mock file** | `shared/mock/mock_rule_alert.json`, `shared/mock/mock_ml_result.json` |

**Yêu cầu:**
- Dashboard đọc từ `shared/output/` hoặc nhận dict trực tiếp
- Hàm entry point: `ui.dashboard.show(rule_result: dict, ml_result: dict)`
- Có thể chạy với mock data bằng `python ui/run_ui.py`

---

## 3. Quy ước kỹ thuật bắt buộc

| Hạng mục | Quy ước |
|---|---|
| Ngôn ngữ | Python 3.10+ |
| Encoding | UTF-8 |
| Field name | snake_case |
| Timestamp | ISO 8601 (`2026-04-03T21:00:00`) |
| Không có data | Trả về `null`, không bỏ trống field |
| Lỗi | In log ra console, không crash cả pipeline |
| Import | Dùng relative import trong package |
| Branch | Mỗi người 1 branch: `feature/capture`, `feature/rule`, `feature/ml`, `feature/ui` |

---

## 4. Thư mục dự án

```
HybridIDS-nhom3/
├── shared/
│   ├── schema.py               # Dataclass định nghĩa tất cả schema
│   ├── output/                 # Module ghi output thật vào đây
│   └── mock/
│       ├── mock_packet.json
│       ├── mock_features.json
│       ├── mock_rule_alert.json
│       └── mock_ml_result.json
├── capture/
│   ├── capture.py
│   └── run_capture.py
├── rule_engine/
│   ├── rule_detector.py
│   └── run_rule.py
├── ml/
│   ├── ml_detector.py
│   ├── train.py
│   ├── model/
│   └── run_ml.py
├── ui/
│   ├── dashboard.py
│   └── run_ui.py
├── main.py                     # Pipeline tích hợp (nhóm trưởng viết)
├── requirements.txt
└── contract.md                 # File này
```

---

## 5. Quy trình thay đổi schema

1. Thành viên tạo issue trên GitHub mô tả field cần thêm/sửa
2. Nhóm trưởng duyệt và cập nhật `schema.py` + `contract.md`
3. Cập nhật mock data tương ứng
4. Thông báo cả nhóm trước khi merge

---

> Cập nhật lần cuối: 2026-04-07 | Nhóm trưởng phụ trách duy trì file này.
