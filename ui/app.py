"""
ui/app.py
=========
Streamlit Dashboard for Hybrid IDS.
Reads alert_log.jsonl and renders real-time metrics, charts, and tables.

Launch: python -m streamlit run ui/app.py
   or:  python ui/run_ui.py --app
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path

st.set_page_config(page_title="Hybrid IDS Dashboard", page_icon="🛡️", layout="wide")

# Use absolute path so it works regardless of CWD
_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = str(_ROOT / "shared" / "output" / "alert_log.jsonl")

# Maximum number of log lines to display (tail optimization)
MAX_DISPLAY_LINES = 200


def load_logs() -> pd.DataFrame:
    """Read alert_log.jsonl and return a DataFrame sorted by timestamp desc."""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    logs = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Tail: only parse the last MAX_DISPLAY_LINES entries
        for line in lines[-MAX_DISPLAY_LINES:]:
            stripped = line.strip()
            if stripped:
                logs.append(json.loads(stripped))
    except (json.JSONDecodeError, OSError) as exc:
        st.error(f"Lỗi đọc log file: {exc}")
        return pd.DataFrame()

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp", ascending=False)
    return df


@st.fragment(run_every="2s")
def render_dashboard():
    """Auto-refreshing dashboard fragment (runs every 2 seconds)."""
    df = load_logs()

    if df.empty:
        st.info("Chưa có dữ liệu log. Đang chờ hệ thống IDS hoạt động...")
        return

    # ── COMPONENT 1: Top Metrics ──────────────────────────────────────
    st.subheader("📊 Tổng quan Hệ thống (Real-time)")
    col1, col2, col3, col4 = st.columns(4)

    total_alerts = len(df)
    high_alerts = len(df[df["severity"] == "high"])
    medium_low_alerts = len(df[df["severity"].isin(["medium", "low"])])
    safe_packets = len(df[df["attack_type"] == "None"])

    col1.metric("Tổng số Logs", total_alerts)
    col2.metric("🟢 Bình thường (None)", safe_packets)
    col3.metric("🔴 Cảnh báo mức HIGH", high_alerts, delta_color="inverse")
    col4.metric("🟠 Cảnh báo mức MEDIUM/LOW", medium_low_alerts, delta_color="inverse")

    # ── COMPONENT 2: Real-time Alert Notification ─────────────────────
    if "last_toast_time" not in st.session_state:
        st.session_state.last_toast_time = None

    latest_high = df[df["severity"] == "high"].head(1)
    if not latest_high.empty:
        latest_record = latest_high.iloc[0]
        record_time = latest_record["timestamp"]
        if st.session_state.last_toast_time != record_time:
            st.toast(
                f"🚨 [{latest_record['attack_type']}] từ IP "
                f"{latest_record['source_ip']} "
                f"(Confidence: {latest_record['confidence'] * 100:.1f}%)",
                icon="🚨",
            )
            st.session_state.last_toast_time = record_time

    st.divider()

    # ── COMPONENT 3 & 4: Chart + Table ────────────────────────────────
    col_chart, col_table = st.columns([1, 2])

    # COMPONENT 3: Attack Distribution Chart
    with col_chart:
        st.subheader("📈 Phân bố loại tấn công")
        attack_counts = (
            df[df["attack_type"] != "None"]["attack_type"]
            .value_counts()
            .reset_index()
        )
        attack_counts.columns = ["attack_type", "count"]

        if not attack_counts.empty:
            st.bar_chart(attack_counts, x="attack_type", y="count", color="#ff4b4b")
        else:
            st.write("Chưa có dữ liệu tấn công.")

    # COMPONENT 4: Live Attack Log Table
    with col_table:
        st.subheader("📋 Live Attack Log (20 records mới nhất)")
        display_cols = [
            "timestamp",
            "source_ip",
            "destination_ip",
            "attack_type",
            "severity",
            "confidence",
        ]
        display_df = df.head(20)[[c for c in display_cols if c in df.columns]]

        def highlight_severity(row):
            if row["severity"] == "high":
                return ["background-color: #ff4b4b; color: white"] * len(row)
            elif row["severity"] == "medium":
                return ["background-color: #ffa500; color: black"] * len(row)
            return [""] * len(row)

        st.dataframe(
            display_df.style.apply(highlight_severity, axis=1),
            use_container_width=True,
            hide_index=True,
        )


# ── Page Layout ───────────────────────────────────────────────────────
st.title("🛡️ Hybrid IDS Dashboard")
st.markdown(
    "Giám sát các cuộc tấn công mạng và hệ thống phát hiện xâm nhập lai "
    "(Rule-based + ML) theo thời gian thực."
)
render_dashboard()
