
import os, json, datetime as dt, pandas as pd, streamlit as st
from utils.digest_formatter import read_queue, build_markdown_summary, build_plaintext_summary
try:
    from utils.email_sendgrid import send_email, SendGridError
except Exception:
    send_email=None; 
    class SendGridError(Exception): ...
st.set_page_config(page_title="Daily Digest", layout="wide"); st.title("Daily Digest")
DIGEST_FILE=os.path.join("alerts","digest_queue.jsonl"); os.makedirs("alerts", exist_ok=True)
rows=read_queue(DIGEST_FILE)
def _rule_name(r): return (r or {}).get("name") or f"{(r or {}).get('metric')} {(r or {}).get('operator')} {(r or {}).get('threshold')}"
all_metrics=sorted({(r.get('rule') or {}).get('metric','') for r in rows}-({''})); all_types=sorted({r.get('type','') for r in rows}-({''}))
fc1,fc2,fc3=st.columns([1,1,2])
with fc1: f_metrics=st.multiselect("Filter metrics", all_metrics, default=all_metrics)
with fc2: f_types=st.multiselect("Filter types", all_types, default=all_types)
with fc3: st.caption("Filters apply to both the table and the summary.")
def _apply_filters(rows, metrics, types):
    out=[]; 
    for r in rows:
        rule=r.get("rule") or {}; metric=rule.get("metric",""); typ=r.get("type","")
        if metrics and metric not in metrics: continue
        if types and typ not in types: continue
        out.append(r)
    return out
rows_f=_apply_filters(rows, f_metrics, f_types)
def _format_rows(rows):
    if not rows: return pd.DataFrame(columns=["ts","type","rule","reason"])
    data=[{"ts":r.get("ts"),"type":r.get("type"),"rule": _rule_name(r.get("rule",{})), "reason": r.get("reason","")} for r in rows]
    df=pd.DataFrame(data); 
    if not df.empty:
        try: df["_ts"]=pd.to_datetime(df["ts"],errors="coerce"); df=df.sort_values("_ts", ascending=False).drop(columns=["_ts"])
        except Exception: pass
    return df
df=_format_rows(rows_f)
c1,c2,c3,c4=st.columns([1,1,1,2])
with c1:
    if st.button("Refresh"): st.experimental_rerun()
with c2:
    if st.button("Clear Queue"):
        try: open(DIGEST_FILE,"w",encoding="utf-8").close(); st.success("Cleared."); st.experimental_rerun()
        except Exception as e: st.error(f"Could not clear: {e}")
with c3:
    txt=build_plaintext_summary(rows_f); st.download_button("Download TXT", data=txt.encode("utf-8"), file_name=f"digest_{dt.date.today().isoformat()}.txt", mime="text/plain")
with c4:
    md=build_markdown_summary(rows_f); st.download_button("Download MD", data=md.encode("utf-8"), file_name=f"digest_{dt.date.today().isoformat()}.md", mime="text/markdown")
st.divider(); st.subheader("Queued Alerts")
st.dataframe(df, use_container_width=True) if not df.empty else st.info("No alerts queued yet.")
st.divider(); st.subheader("Summary Preview"); st.markdown(md)


# --- [78] Subject prefix + Latest send status + custom send/rebuild ---
import streamlit as _st
from utils.jobs_history import read_jobs
try:
    from utils.digest_runner import send_latest_digest as _send_latest, run_digest as _run_digest
except Exception:
    _send_latest = None
    _run_digest = None

_st.subheader("Subject Prefix")
if "digest_subject_prefix" not in _st.session_state:
    _st.session_state["digest_subject_prefix"] = "Vega Daily Digest"
prefix = _st.text_input("Email subject prefix", value=_st.session_state["digest_subject_prefix"])
_st.session_state["digest_subject_prefix"] = prefix

_st.subheader("Latest Send Status")
try:
    rows = read_jobs()
    cand = [r for r in rows if r.get("job") in ("digest_run","digest_send_latest")]
    last = cand[-1] if cand else {}
    stts = last.get("status","—")
    ts = (last.get("ts","") or "").replace("T"," ").replace("Z","")
    _st.write(f"**Last:** {ts} | **Status:** {stts}")
except Exception:
    _st.info("No digest history yet.")

col1, col2 = _st.columns(2)
if _send_latest:
    if col1.button("Send Latest (use subject above)", use_container_width=True):
        res = _send_latest(prefix)
        _st.write(res)
else:
    col1.button("Send Latest unavailable", disabled=True, use_container_width=True)

if _run_digest:
    if col2.button("Rebuild + Email (use subject above)", type="primary", use_container_width=True):
        res = _run_digest(prefix + " (Rebuild)")
        _st.write(res)
else:
    col2.button("Rebuild unavailable", disabled=True, use_container_width=True)
