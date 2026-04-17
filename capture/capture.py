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


def _packet_to_event(pkt: Any, duration: float) -> dict:
    """Chuyển 1 scapy packet thành PacketEvent dict hợp lệ."""
    from scapy.all import ICMP, IP, IPv6, TCP, UDP

    if IP in pkt:
        ip_layer = pkt[IP]
        src_ip = str(ip_layer.src)
        dst_ip = str(ip_layer.dst)
    elif IPv6 in pkt:
        ip_layer = pkt[IPv6]
        src_ip = str(ip_layer.src)
        dst_ip = str(ip_layer.dst)
    else:
        src_ip = "0.0.0.0"
        dst_ip = "0.0.0.0"

    src_port = 0
    dst_port = 0
    flags = "NONE"
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
        "duration": max(0.0, float(duration)),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    return _build_packet_event(data).to_dict()


def _sniff_packets(
    iface: Optional[str],
    timeout: int,
    packet_filter: Optional[str],
    count: int,
) -> list[Any]:
    """Thực hiện sniff và trả về danh sách packet thô từ Scapy."""
    try:
        from scapy.all import sniff
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
    return list(packets)


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
    return_batch: bool = False,
) -> dict | list[dict]:
    """
    Sniff packet thật.

    Mặc định trả về 1 PacketEvent (packet cuối) để tương thích pipeline cũ.
    Nếu return_batch=True thì trả về list PacketEvent và ghi thêm packet_events.json.

    Args:
        iface: tên card mạng (None = default interface)
        timeout: số giây chờ packet
        packet_filter: BPF filter, ví dụ "tcp", "udp", "host 8.8.8.8"
        count: số packet tối đa cần bắt trong một phiên sniff
    """
    packets = _sniff_packets(
        iface=iface,
        timeout=timeout,
        packet_filter=packet_filter,
        count=count,
    )
    events: list[dict] = []
    previous_time: Optional[float] = None
    for pkt in packets:
        current_time = float(pkt.time)
        if previous_time is None:
            delta = 0.0
        else:
            delta = current_time - previous_time
        events.append(_packet_to_event(pkt, delta))
        previous_time = current_time

    last_event = events[-1]

    out_path = get_output_path("packet_event.json")
    save_json(last_event, out_path)

    if return_batch:
        batch_out_path = get_output_path("packet_events.json")
        save_json(events, batch_out_path)
        return events

    return last_event


def capture_packets_live(
    iface: Optional[str] = None,
    timeout: int = 10,
    packet_filter: Optional[str] = None,
    count: int = 10,
) -> list[dict]:
    """Sniff và trả về danh sách PacketEvent (batch mode)."""
    return capture_packet_live(
        iface=iface,
        timeout=timeout,
        packet_filter=packet_filter,
        count=count,
        return_batch=True,
    )


def list_capture_interfaces() -> list[str]:
    """Liệt kê các interface có thể sniff bằng Scapy."""
    try:
        from scapy.all import get_if_list
    except Exception as exc:
        raise RuntimeError(
            "Không import được scapy. Hãy cài dependencies: pip install -r requirements.txt"
        ) from exc
    return sorted(get_if_list())


def capture_packet(mode: str = "mock", **kwargs) -> dict | list[dict]:
    """
    Entry point của module Data Capture.

    Returns:
        dict | list[dict]: PacketEvent đơn hoặc danh sách PacketEvent (khi return_batch=True)
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
            return_batch=bool(kwargs.get("return_batch", False)),
        )
    raise ValueError(f"Mode không hợp lệ: {mode}. Dùng 'mock' hoặc 'live'.")