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

## Chạy từng module độc lập (để test)

```bash
# TV1 — Data Capture
python capture/run_capture.py

# TV2 — Rule-based Detection
python rule_engine/run_rule.py

# TV3 — Machine Learning (train model trước)
python ml/train.py
python ml/run_ml.py

# TV4 — UI Dashboard
streamlit run ui/run_ui.py
```

---

## Chạy toàn bộ pipeline

```bash
python main.py
```

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
| Data Capture | TV1 | `feature/capture` |
| Rule-based Detection | TV2 | `feature/rule` |
| Machine Learning | TV3 | `feature/ml` |
| UI + Integration | TV4 | `feature/ui` |

---

## Quy ước

- Tất cả module giao tiếp qua JSON (xem `contract.md`)
- Không tự sửa `shared/schema.py` — báo nhóm trưởng trước
- Mỗi module phải chạy được độc lập với mock data trước khi merge