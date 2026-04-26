from collections import defaultdict
from datetime import datetime, timedelta

from .config import CONFIG


class RuleEngine:
    def __init__(self):
        self.syn_tracker = defaultdict(list)
        self.traffic_tracker = defaultdict(list)
        self.login_tracker = defaultdict(list)

    # Entry point chính — gọi hàm này cho mỗi packet
    def analyze(self, packet: dict) -> dict:
        alerts = []
        alerts += self._detect_port_scan(packet)
        alerts += self._detect_dos(packet)
        alerts += self._detect_brute_force(packet)

        return {
            "alert": len(alerts) > 0,
            "alerts": alerts,
            "src_ip": packet.get("src_ip"),
        }

    # Rule 1: Port Scan
    # Dấu hiệu: 1 IP gửi SYN đến nhiều port khác nhau
    def _detect_port_scan(self, packet: dict) -> list:
        if packet.get("flags") != "SYN":
            return []

        cfg = CONFIG["port_scan"]
        src = packet["src_ip"]
        now = datetime.fromisoformat(packet["timestamp"])
        dst_port = packet.get("dst_port")

        self.syn_tracker[src].append((now, dst_port))

        window = timedelta(seconds=cfg["window_sec"])
        self.syn_tracker[src] = [(t, p) for t, p in self.syn_tracker[src] if now - t <= window]

        ports = set(p for _, p in self.syn_tracker[src])
        if len(ports) >= cfg["threshold"]:
            return [
                {
                    "type": "Port Scan",
                    "src_ip": src,
                    "detail": f"{len(ports)} ports scanned in {cfg['window_sec']}s",
                }
            ]
        return []

    # Rule 2: DoS
    # Dấu hiệu: 1 IP gửi quá nhiều packet trong 1 giây
    def _detect_dos(self, packet: dict) -> list:
        cfg = CONFIG["dos"]
        src = packet["src_ip"]
        now = datetime.fromisoformat(packet["timestamp"])

        self.traffic_tracker[src].append(now)

        window = timedelta(seconds=cfg["window_sec"])
        self.traffic_tracker[src] = [t for t in self.traffic_tracker[src] if now - t <= window]

        count = len(self.traffic_tracker[src])
        if count >= cfg["threshold"]:
            return [
                {
                    "type": "DoS",
                    "src_ip": src,
                    "detail": f"{count} packets in {cfg['window_sec']}s",
                }
            ]
        return []

    # Rule 3: Brute Force
    # Dấu hiệu: 1 IP kết nối liên tục đến SSH/FTP/RDP
    def _detect_brute_force(self, packet: dict) -> list:
        cfg = CONFIG["brute_force"]
        if packet.get("dst_port") not in cfg["target_ports"]:
            return []

        src = packet["src_ip"]
        now = datetime.fromisoformat(packet["timestamp"])

        self.login_tracker[src].append(now)

        window = timedelta(seconds=cfg["window_sec"])
        self.login_tracker[src] = [t for t in self.login_tracker[src] if now - t <= window]

        count = len(self.login_tracker[src])
        if count >= cfg["threshold"]:
            return [
                {
                    "type": "Brute Force",
                    "src_ip": src,
                    "detail": f"{count} attempts to port {packet['dst_port']} in {cfg['window_sec']}s",
                }
            ]
        return []