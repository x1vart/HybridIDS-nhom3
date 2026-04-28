"""
ui/app.py
=========
Streamlit Dashboard for Hybrid IDS.
Reads alert_log.jsonl (production) or alert_log_test.jsonl (mock) and renders real-time metrics, charts, and tables.

Launch: python -m streamlit run ui/app.py
   or:  python ui/run_ui.py --app
"""

import json
import os
from collections import deque
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hybrid IDS Dashboard", page_icon="🛡️", layout="wide")

_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = str(_ROOT / "shared" / "output" / "alert_log.jsonl")
TEST_LOG_FILE = str(_ROOT / "shared" / "output" / "alert_log_test.jsonl")
MAX_DISPLAY_LINES = 200
SOURCE_OPTIONS = {
    "Production": LOG_FILE,
    "Mock": TEST_LOG_FILE,
}


def render_sidebar():
    """Render sidebar controls and return mode plus filters."""
    st.subheader("⚙️ Điều khiển")

    data_source = st.selectbox(
        "Data source",
        options=list(SOURCE_OPTIONS.keys()),
        index=0,
        help="Chọn Mock để xem alert_log_test.jsonl hoặc Production để xem alert_log.jsonl.",
    )
    test_mode = data_source == "Mock"

    st.caption(f"Đang đọc: {SOURCE_OPTIONS[data_source]}")

    if st.button("🗑️ Clear current log", use_container_width=True):
        log_file = SOURCE_OPTIONS[data_source]
        if os.path.exists(log_file):
            os.remove(log_file)
            st.success("Log cleared!")
            st.rerun()
        else:
            st.info("Log file not found or already empty.")

    st.divider()
    st.subheader("🔍 Bộ lọc")

    severity_filter = st.multiselect(
        "Severity",
        options=["high", "medium", "low"],
        default=["high", "medium", "low"],
    )
    attack_filter = st.multiselect(
        "Attack type",
        options=["Port Scan", "DoS", "Brute Force", "None"],
        default=["Port Scan", "DoS", "Brute Force", "None"],
    )
    return test_mode, severity_filter, attack_filter


def load_logs(test_mode: bool = False) -> pd.DataFrame:
    """Read the chosen log file and return a DataFrame sorted by timestamp desc."""
    log_file = TEST_LOG_FILE if test_mode else LOG_FILE
    if not os.path.exists(log_file):
        return pd.DataFrame()

    logs = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in deque(f, maxlen=MAX_DISPLAY_LINES):
                stripped = line.strip()
                if stripped:
                    logs.append(json.loads(stripped))
    except Exception as exc:
        st.error(f"Error reading log: {exc}")
        return pd.DataFrame()

    df = pd.DataFrame(logs)
    if df.empty:
        return df

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp", ascending=False)
    return df


@st.fragment(run_every="2s")
def render_dashboard(test_mode: bool, severity_filter: list[str], attack_filter: list[str]):
    """Auto-refreshing dashboard fragment."""
    df = load_logs(test_mode=test_mode)

    if not df.empty:
        if "severity" in df.columns and severity_filter:
            df = df[df["severity"].isin(severity_filter)]
        if "attack_type" in df.columns and attack_filter:
            df = df[df["attack_type"].isin(attack_filter)]

    if df.empty:
        st.warning("No alerts yet. Waiting for data...")
        return

    for col, default in {
        "severity": "low",
        "attack_type": "None",
        "source_ip": "0.0.0.0",
        "destination_ip": "0.0.0.0",
        "confidence": 0.0,
    }.items():
        if col not in df.columns:
            df[col] = default

    st.caption("Realtime view cập nhật mỗi 2 giây.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alerts", len(df))
    with col2:
        st.metric("Safe", int((df["severity"] == "low").sum()))
    with col3:
        high_count = int((df["severity"] == "high").sum())
        st.metric("High Risk", high_count, delta="🔴" if high_count > 0 else "")
    with col4:
        medium_count = int((df["severity"] == "medium").sum())
        st.metric("Medium Risk", medium_count, delta="🟡" if medium_count > 0 else "")

    most_recent = df.iloc[0]
    if most_recent.get("severity") == "high":
        confidence = most_recent.get("confidence", 0.0)
        confidence_pct = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "N/A"
        st.warning(
            f"🚨 **HIGH ALERT** ({confidence_pct}): {most_recent.get('attack_type', 'Unknown')} from {most_recent.get('source_ip', 'Unknown')}"
        )

    st.subheader("Attack Distribution")
    st.bar_chart(df["attack_type"].value_counts())

    st.subheader("Alert Log (Recent 20)")
    display_cols = [
        "timestamp",
        "severity",
        "attack_type",
        "source_ip",
        "destination_ip",
        "confidence",
    ]
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].head(20).copy()
    if "confidence" in display_df.columns:
        display_df["confidence"] = display_df["confidence"].apply(
            lambda x: f"{x * 100:.1f}%" if isinstance(x, (int, float)) else str(x)
        )

    st.dataframe(display_df, use_container_width=True, height=400)


def main():
    st.title("🛡️ Hybrid IDS Dashboard")
    with st.sidebar:
        test_mode, severity_filter, attack_filter = render_sidebar()
    render_dashboard(test_mode, severity_filter, attack_filter)


if __name__ == "__main__":
    main()
