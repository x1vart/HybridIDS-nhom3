"""
shared/utils.py
===============
Các hàm tiện ích dùng chung cho toàn bộ hệ thống IDS.
Import từ đây thay vì tự viết lại trong từng module.

Cách dùng:
    from shared.utils import load_json, save_json, now_iso, get_output_path, to_json
"""

import json
import os
from datetime import datetime


# ──────────────────────────────────────────────
# Thời gian
# ──────────────────────────────────────────────

def now_iso() -> str:
    """Trả về timestamp hiện tại theo chuẩn ISO 8601."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def to_json(obj) -> str:
    """Serialize object (ưu tiên dataclass) sang JSON string."""
    if hasattr(obj, "to_dict"):
        payload = obj.to_dict()
    elif hasattr(obj, "__dict__"):
        payload = obj.__dict__
    else:
        payload = obj
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Đọc / Ghi JSON
# ──────────────────────────────────────────────

def load_json(path: str) -> dict:
    """
    Đọc file JSON, trả về dict.
    Báo lỗi rõ ràng nếu file không tồn tại hoặc sai format.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"[utils] Không tìm thấy file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"[utils] File JSON bị lỗi format: {path}\n{e}")


def save_json(data: dict, path: str) -> None:
    """
    Ghi dict ra file JSON.
    Tự tạo thư mục cha nếu chưa tồn tại.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[utils] ✅ Đã ghi: {path}")


def append_json_log(data: dict, path: str) -> None:
    """
    Thêm 1 bản ghi vào file log dạng JSON array.
    Nếu file chưa tồn tại thì tạo mới.
    Dùng cho Alert & Logging module (TV4).
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logs = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def to_json(data: any) -> str:
    """
    Chuyển đổi object/dict thành chuỗi JSON.
    (Hàm này được thêm vào để vá lỗi cho class MLResult)
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Đường dẫn
# ──────────────────────────────────────────────

# Thư mục gốc project (ids-project/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_output_path(filename: str) -> str:
    """
    Trả về đường dẫn đầy đủ tới shared/output/<filename>.
    Dùng khi muốn ghi output mà không cần nhớ đường dẫn tuyệt đối.
    """
    return os.path.join(BASE_DIR, "shared", "output", filename)


def get_mock_path(filename: str) -> str:
    """
    Trả về đường dẫn đầy đủ tới shared/mock/<filename>.
    Dùng trong các file run_xxx.py để load mock data.
    """
    return os.path.join(BASE_DIR, "shared", "mock", filename)


# ──────────────────────────────────────────────
# Quick test
# python shared/utils.py
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("output path:", get_output_path("test.json"))
    print("mock path  :", get_mock_path("mock_packet.json"))
    print("now_iso    :", now_iso())

    # Test ghi/đọc
    save_json({"test": True, "time": now_iso()}, get_output_path("_test.json"))
    data = load_json(get_output_path("_test.json"))
    print("Đọc lại:", data)
    print("✅ utils.py hoạt động bình thường")