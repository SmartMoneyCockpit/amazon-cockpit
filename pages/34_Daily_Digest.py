
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


import streamlit as st
from utils.jobs_history import read_jobs
try:
    from utils.digest_runner import run_digest
except Exception:
    run_digest=None

st.subheader("Digest Status")
try:
    rows=read_jobs(); cand=[r for r in rows if r.get("job")=="digest_run"]
    last=cand[-1] if cand else {}
    st.write(f"**Last Attempt:** {last.get('ts','—')} | **Status:** {last.get('status','—')}")
except Exception:
    st.info("No digest history yet.")

if st.button("Run Digest Now", type="primary", use_container_width=True) and run_digest:
    res=run_digest(subject_prefix="Vega Daily Digest (Manual)")
    st.write(res)
