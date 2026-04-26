# ============================================================
# Module 2 - Rule-Based Detection
# Config: chỉnh threshold ở đây, không cần đụng code chính
# ============================================================

CONFIG = {
    "port_scan": {
        "threshold": 20,        # số port khác nhau từ 1 IP
        "window_sec": 5         # trong khoảng thời gian (giây)
    },
    "dos": {
        "threshold": 1000,      # số packet từ 1 IP
        "window_sec": 1         # trong khoảng thời gian (giây)
    },
    "brute_force": {
        "threshold": 10,        # số lần kết nối
        "window_sec": 10,       # trong khoảng thời gian (giây)
        "target_ports": [22, 21, 3389]  # SSH, FTP, RDP
    }
}