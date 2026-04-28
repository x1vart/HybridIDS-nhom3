# HybridIDS-nhom3 — Intrusion Detection System

Hệ thống phát hiện xâm nhập mạng sử dụng Rule-based + Machine Learning.

---

## Yêu cầu

- Python 3.10+
- (Khuyến nghị) Linux hoặc WSL để capture packet thật

---

## Cài đặt

```bash
# 1. Clone repo
git clone https://github.com/kien055/HybridIDS-nhom3.git
cd HybridIDS-nhom3

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Cài thư viện
pip install -r requirements.txt
```

---
## Dùng CICIDS2017 cho ML

ML của project không đọc raw CSV CICIDS2017 trực tiếp. Dữ liệu phải được convert sang đúng format `FeatureVector` trong `contract.md` và `shared/schema.py` trước khi chạy `ml/run_ml.py`.

### Luồng chạy

```bash
# 1. Convert CSV CICIDS2017 sang JSON feature
python ml/prepare_cicids.py --csv "path/to/your_cicids.csv" --max-rows 500

# 2. Chạy ML với file đã convert
python ml/run_ml.py --input shared/mock/cicids_features.json --index 0
```

### Nếu muốn thay mock test hiện tại

```bash
python ml/prepare_cicids.py --csv "path/to/your_cicids.csv" --replace-mock
python ml/run_ml.py
```

Lưu ý: `--replace-mock` sẽ ghi đè `shared/mock/mock_features.json`, nên có thể ảnh hưởng phần test của Rule-based nếu team đang dùng chung file này.

### Mapping CICIDS2017 -> FeatureVector

Script `ml/prepare_cicids.py` đang map các cột phổ biến như sau:

| CICIDS2017 | FeatureVector |
|---|---|
| `Source IP` / `Src IP` | `src_ip` |
| `Destination IP` / `Dst IP` | `dst_ip` |
| `Destination Port` / `Dst Port` | `dst_port` |
| `Protocol` | `protocol` |
| `Total Fwd Packets` + `Total Backward Packets` | `packet_count` |
| `Flow Duration` / `Duration` | `connection_duration` |
| `Average Packet Size` / `Packet Length Mean` / `Avg Packet Size` | `avg_packet_size` |
| `SYN Flag Count` / `ACK Flag Count` / `FIN Flag Count` / `RST Flag Count` / `PSH Flag Count` / `URG Flag Count` | `flags` |
| `Timestamp` / `timestamp` | `timestamp` |

### Ghi chú

- Nếu CSV có nhiều dòng, `ml/prepare_cicids.py` sẽ xuất ra một file JSON list.
- Dùng `--index` để chọn 1 dòng cụ thể khi test.
- Đây là lớp chuyển đổi để test theo schema của project, không phải giữ nguyên raw format CICIDS.

```bash
# Convert toi da 500 dong tu CICIDS2017 CSV
python ml/prepare_cicids.py --csv "path/to/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" --max-rows 500

# Neu muon thay hẳn shared/mock/mock_features.json bang dong dau tien
python ml/prepare_cicids.py --csv "path/to/file.csv" --replace-mock
```

Sau khi convert, chay ML voi file moi:

```bash
# Chay voi dong dau tien trong danh sach converted
python ml/run_ml.py --input shared/mock/cicids_features.json --index 0

# Hoac chay theo mock cu (neu da --replace-mock)
python ml/run_ml.py
```

---

## Chạy toàn bộ pipeline

```bash
python main.py
```

---

## Chạy riêng Data Capture

### 1) Chạy mock (an toàn, không cần quyền Admin)

```bash
python capture/run_capture.py --mode mock
```

Kết quả sẽ được ghi tại `shared/output/packet_event.json`.

### 2) Xem danh sách interface để capture thật

```bash
python capture/run_capture.py --list-ifaces
```

### 3) Capture packet thật (live mode)

```bash
python capture/run_capture.py --mode live --iface "Wi-Fi" --timeout 15 --filter tcp --count 5
```

Ý nghĩa tham số:

- `--iface`: tên card mạng, lấy từ `--list-ifaces`
- `--timeout`: thời gian chờ tối đa (giây)
- `--filter`: bộ lọc BPF (vd: `tcp`, `udp`, `host 8.8.8.8`)
- `--count`: số packet muốn bắt trong 1 phiên

Lưu ý Windows:

- Nên mở terminal bằng quyền Administrator.
- Nên cài Npcap để sniff ổn định với Scapy.
- Nếu timeout mà không có traffic, hãy mở web/ping để tạo lưu lượng trước khi chạy capture.

---

## Cấu trúc thư mục

```
HybridIDS-nhom3/
├── shared/
│   ├── schema.py          # Định nghĩa dataclass dùng chung
│   ├── utils.py           # Hàm load/save JSON, đường dẫn
│   ├── output/            # Kết quả thật (không commit lên Git)
│   └── mock/              # Dữ liệu giả để test từng module
├── capture/               # Module bắt packet (TV1)
├── rule_engine/           # Module rule-based detection (TV2)
├── ml/                    # Module machine learning (TV3)
├── ui/                    # Dashboard + tích hợp (TV4)
├── main.py                # Pipeline tích hợp toàn bộ
├── contract.md            # Chuẩn giao tiếp giữa các module
└── requirements.txt
```

---

## Phân công

| Module | Thành viên | Branch |
|---|---|---|
| Data Capture | Kien | `feature/capture` |
| Rule-based Detection | Tung | `feature/rule` |
| Machine Learning | Viet | `feature/ml` |
| UI + Integration | Thuan | `feature/ui` |

---

## Quy ước

- Tất cả module giao tiếp qua JSON (xem `contract.md`)
- Không tự sửa `shared/schema.py` — báo nhóm trưởng trước
- Mỗi module phải chạy được độc lập với mock data trước khi merge