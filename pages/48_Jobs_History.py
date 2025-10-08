
import io, datetime as dt, json, pandas as pd, streamlit as st
from utils.jobs_history import read_jobs, filter_jobs, read_jobs_raw, extract_error_snippet
st.set_page_config(page_title="Jobs History", layout="wide"); st.title("Jobs History")
LOG_FILE="logs/vega_jobs.jsonl"; rows=read_jobs(LOG_FILE)
all_jobs=sorted({r.get("job","") for r in rows}-{""}); all_statuses=sorted({r.get("status","") for r in rows}-{""})
c1,c2,c3,c4=st.columns([1.2,1.2,1.2,1.4])
with c1: sel_jobs=st.multiselect("Jobs", all_jobs, default=all_jobs)
with c2: sel_status=st.multiselect("Status", all_statuses, default=all_statuses)
with c3: date_from=st.date_input("From", value=(dt.date.today()-dt.timedelta(days=14)))
with c4: date_to=st.date_input("To", value=dt.date.today())
rows_f=filter_jobs(rows, sel_jobs, sel_status, date_from, date_to)
def _mk_df(rows):
    if not rows: return pd.DataFrame(columns=["ts","job","status","detail"])
    df=pd.DataFrame(rows)
    for col in ["ts","job","status","detail"]:
        if col not in df.columns: df[col]=""
    try: df["_ts"]=pd.to_datetime(df["ts"],errors="coerce"); df=df.sort_values("_ts", ascending=False).drop(columns=["_ts"])
    except Exception: pass
    return df[["ts","job","status","detail"]]
df=_mk_df(rows_f)
k1,k2,k3=st.columns(3)
k1.metric("Total runs", f"{len(rows_f):,}"); k2.metric("Successes", f"{sum(1 for r in rows_f if r.get('status')=='ok'): ,}"); k3.metric("Failures", f"{sum(1 for r in rows_f if r.get('status')=='error'): ,}")
st.divider(); st.subheader("Run History")
st.dataframe(df, use_container_width=True) if not df.empty else st.info("No job runs yet.")
st.divider(); st.subheader("Per-Run Details")
options=[f"{r.get('ts','')} — {r.get('job','')} ({r.get('status','')})" for r in rows_f]
idx=st.selectbox("Select a run", options=list(range(len(options))), format_func=lambda i: options[i] if options else "", index=0 if options else 0)
if options:
    rec=rows_f[idx]
    cdt1,cdt2=st.columns([2,2])
    with cdt1: st.markdown("**Record JSON**"); st.code(json.dumps(rec, indent=2, ensure_ascii=False))
    with cdt2: st.markdown("**Error / Detail Snippet**"); st.code(extract_error_snippet(rec) or "(no detail)")
    st.download_button("Download record JSON", data=json.dumps(rec, ensure_ascii=False).encode("utf-8"), file_name=f"job_record_{rec.get('job','')}_{rec.get('ts','')}.json", mime="application/json")
st.divider(); st.subheader("Raw Log Tail (debug)")
raw_lines=read_jobs_raw(LOG_FILE); tail_n=st.slider("Show last N lines", 10, 500, 80, 10)
st.code("\n".join(raw_lines[-tail_n:])) if raw_lines else st.caption("No raw log lines yet.")


# --- [76] Only today + hourly sparkline ---
import streamlit as _st
import pandas as _pd
from datetime import date as _date, datetime as _dt
from utils.jobs_history import read_jobs

_st.subheader("Only Today + Hourly Runs")
rows = read_jobs()
only_today = _st.toggle("Only today", value=True)
series = [r for r in rows if True]
if only_today:
    today = _date.today()
    tmp = []
    for r in rows:
        ts = (r.get("ts") or "")
        try:
            t = _dt.fromisoformat(ts.replace("Z",""))
            if t.date() == today:
                tmp.append(r)
        except Exception:
            pass
    series = tmp
# build hourly counts
counts = {}
for r in series:
    ts = (r.get("ts") or "")
    try:
        t = _dt.fromisoformat(ts.replace("Z",""))
        hh = t.strftime("%H:00")
        counts[hh] = counts.get(hh, 0) + 1
    except Exception:
        pass
if counts:
    # ensure all 24 hours show
    idx = [f"{i:02d}:00" for i in range(24)]
    df = _pd.DataFrame({"hour": idx, "runs": [_pd.Series(counts).reindex(idx, fill_value=0)[h] for h in idx]})
    df = df.set_index("hour")
    _st.line_chart(df, use_container_width=True)
else:
    _st.info("No runs logged for the selected window.")
