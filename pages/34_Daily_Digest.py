import os
import json
import datetime as dt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Daily Digest", layout="wide")
st.title("Daily Digest")

DIGEST_FILE = os.path.join("alerts", "digest_queue.jsonl")
os.makedirs("alerts", exist_ok=True)

def _read_queue(path: str):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # skip corrupted lines
                continue
    return rows

def _format_rows(rows):
    if not rows:
        return pd.DataFrame(columns=["ts", "type", "rule", "reason"])
    def _rule_name(r):
        if not isinstance(r, dict):
            return ""
        return r.get("name") or f"{r.get('metric')} {r.get('operator')} {r.get('threshold')}"
    data = []
    for r in rows:
        ts = r.get("ts")
        typ = r.get("type")
        rule = r.get("rule", {})
        reason = r.get("reason", "")
        data.append({
            "ts": ts,
            "type": typ,
            "rule": _rule_name(rule),
            "reason": reason,
        })
    df = pd.DataFrame(data)
    if not df.empty:
        # Sort newest first
        try:
            df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts_parsed", ascending=False).drop(columns=["ts_parsed"])
        except Exception:
            pass
    return df

rows = _read_queue(DIGEST_FILE)
df = _format_rows(rows)

# Controls
c1, c2, c3 = st.columns([1,1,2])
with c1:
    if st.button("Refresh"):
        st.experimental_rerun()
with c2:
    if st.button("Clear Queue"):
        try:
            open(DIGEST_FILE, "w", encoding="utf-8").close()
            st.success("Digest queue cleared.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Could not clear queue: {e}")

st.divider()
st.subheader("Queued Alerts")
if df.empty:
    st.info("No alerts queued yet. Use Alerts Center → Evaluate Now to add items.")
else:
    st.dataframe(df, use_container_width=True)

    # Export helpers
    st.markdown("### Export")
    export_col1, export_col2 = st.columns([1,1])
    with export_col1:
        csv_name = f"digest_export_{dt.date.today().isoformat()}.csv"
        st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name=csv_name, mime="text/csv")
    with export_col2:
        json_name = f"digest_export_{dt.date.today().isoformat()}.jsonl"
        jsonl = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
        st.download_button("Download JSONL", data=jsonl.encode("utf-8"),
                           file_name=json_name, mime="application/json")
