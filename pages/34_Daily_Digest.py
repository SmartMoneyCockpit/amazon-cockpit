import os, json, datetime as dt
import pandas as pd
import streamlit as st
from utils.digest_formatter import read_queue, build_markdown_summary, build_plaintext_summary

st.set_page_config(page_title="Daily Digest", layout="wide")
st.title("Daily Digest")

DIGEST_FILE = os.path.join("alerts", "digest_queue.jsonl")
os.makedirs("alerts", exist_ok=True)

rows = read_queue(DIGEST_FILE)

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
        try:
            df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts_parsed", ascending=False).drop(columns=["ts_parsed"])
        except Exception:
            pass
    return df

df = _format_rows(rows)

# Controls
c1, c2, c3, c4 = st.columns([1,1,1,2])
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
with c3:
    # Build text summary (markdown + plaintext)
    md_summary = build_markdown_summary(rows)
    txt_summary = build_plaintext_summary(rows)
    # Copy to clipboard via HTML/JS (Streamlit component)
    st.download_button(
        "Download TXT",
        data=txt_summary.encode("utf-8"),
        file_name=f"digest_{dt.date.today().isoformat()}.txt",
        mime="text/plain"
    )
with c4:
    # Show a copy button using a tiny HTML/JS component
    st.markdown("")
    st.markdown("")
    html = f'''
    <button id="copyBtn" style="padding:6px 12px;border-radius:6px;border:1px solid #ddd;cursor:pointer;">
        Copy Summary
    </button>
    <script>
    const txt = `{txt_summary.replace("`","\`").replace("\n","\\n")}`;
    const btn = document.getElementById('copyBtn');
    btn.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText(txt);
            btn.innerText = "Copied!";
            setTimeout(() => btn.innerText = "Copy Summary", 1200);
        }} catch (e) {{
            btn.innerText = "Copy failed";
            setTimeout(() => btn.innerText = "Copy Summary", 1200);
        }}
    }});
    </script>
    '''
    st.components.v1.html(html, height=40)

st.divider()
st.subheader("Queued Alerts")
if df.empty:
    st.info("No alerts queued yet. Use Alerts Center → Evaluate Now to add items.")
else:
    st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("Summary Preview")
st.markdown(md_summary)
