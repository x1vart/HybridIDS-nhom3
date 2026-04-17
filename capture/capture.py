"""
capture/capture.py
==================
Data Capture module hỗ trợ 2 chế độ:

- mock: đọc packet từ shared/mock/mock_packet.json
- live: sniff packet thật từ network interface (Scapy)

Output luôn được chuẩn hóa theo shared.schema.PacketEvent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from shared.schema import PacketEvent
from shared.utils import get_mock_path, get_output_path, load_json, save_json


def _normalize_protocol(proto: Any) -> str:
    if proto is None:
        return "TCP"
    proto_text = str(proto).upper()
    if proto_text in {"TCP", "UDP", "ICMP"}:
        return proto_text
    return "TCP"


def _build_packet_event(data: dict) -> PacketEvent:
    """Build + validate PacketEvent để dùng chung giữa mock/live."""
    event = PacketEvent(**data)
    event.validate()
    return event


def capture_packet_mock() -> dict:
    """Capture packet từ mock JSON."""
    data = load_json(get_mock_path("mock_packet.json"))
    event = _build_packet_event(data)

    out_path = get_output_path("packet_event.json")
    save_json(event.to_dict(), out_path)
    return event.to_dict()


def capture_packet_live(
    iface: Optional[str] = None,
    timeout: int = 10,
    packet_filter: Optional[str] = None,
    count: int = 1,
) -> dict:
    """
    Sniff packet thật và trả về packet đầu tiên (chuẩn PacketEvent).

    Args:
        iface: tên card mạng (None = default interface)
        timeout: số giây chờ packet
        packet_filter: BPF filter, ví dụ "tcp", "udp", "host 8.8.8.8"
        count: số packet tối đa cần bắt trong một phiên sniff
    """
    try:
        from scapy.all import ICMP, IP, TCP, UDP, sniff
    except Exception as exc:
        raise RuntimeError(
            "Không import được scapy. Hãy cài dependencies: pip install -r requirements.txt"
        ) from exc

    sniff_count = max(1, int(count))
    try:
        packets = sniff(
            iface=iface,
            count=sniff_count,
            timeout=timeout,
            filter=packet_filter,
        )
    except Exception as exc:
        raise RuntimeError(
            "Sniff thất bại. Hãy chạy terminal bằng quyền Admin và cài Npcap trên Windows."
        ) from exc

    if not packets:
        raise TimeoutError(
            "Không bắt được packet nào trong thời gian chờ. "
            "Thử tăng timeout hoặc đổi interface/filter."
        )

    pkt = packets[-1]
    capture_duration = 0.0
    if len(packets) >= 2:
        capture_duration = max(0.0, float(packets[-1].time) - float(packets[0].time))

    if IP in pkt:
        ip_layer = pkt[IP]
        src_ip = str(ip_layer.src)
        dst_ip = str(ip_layer.dst)
    else:
        src_ip = "0.0.0.0"
        dst_ip = "0.0.0.0"

    src_port = 0
    dst_port = 0
    flags = ""
    protocol = "TCP"

    if TCP in pkt:
        tcp_layer = pkt[TCP]
        src_port = int(tcp_layer.sport)
        dst_port = int(tcp_layer.dport)
        protocol = "TCP"
        flags = str(tcp_layer.flags)
    elif UDP in pkt:
        udp_layer = pkt[UDP]
        src_port = int(udp_layer.sport)
        dst_port = int(udp_layer.dport)
        protocol = "UDP"
    elif ICMP in pkt:
        protocol = "ICMP"

    data = {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": _normalize_protocol(protocol),
        "packet_size": int(len(pkt)),
        "flags": flags,
        "duration": capture_duration,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    event = _build_packet_event(data)

    out_path = get_output_path("packet_event.json")
    save_json(event.to_dict(), out_path)
    return event.to_dict()


def list_capture_interfaces() -> list[str]:
    """Liệt kê các interface có thể sniff bằng Scapy."""
    try:
        from scapy.all import get_if_list
    except Exception as exc:
        raise RuntimeError(
            "Không import được scapy. Hãy cài dependencies: pip install -r requirements.txt"
        ) from exc
    return sorted(get_if_list())


def capture_packet(mode: str = "mock", **kwargs) -> dict:
    """
    Entry point của module Data Capture.

    Returns:
        dict: PacketEvent dạng dict (đúng schema trong contract.md)
    """
    selected_mode = mode.strip().lower()
    if selected_mode == "mock":
        return capture_packet_mock()
    if selected_mode == "live":
        return capture_packet_live(
            iface=kwargs.get("iface"),
            timeout=int(kwargs.get("timeout", 10)),
            packet_filter=kwargs.get("packet_filter"),
            count=int(kwargs.get("count", 1)),
        )
    raise ValueError(f"Mode không hợp lệ: {mode}. Dùng 'mock' hoặc 'live'.")