
import io, datetime as dt
import pandas as pd
import streamlit as st
from utils.jobs_history import read_jobs, filter_jobs

st.set_page_config(page_title="Jobs History", layout="wide")
st.title("Jobs History")

LOG_FILE = "logs/vega_jobs.jsonl"

rows = read_jobs(LOG_FILE)

# Build options from data
all_jobs = sorted({ r.get("job","") for r in rows if isinstance(r, dict) } - {""})
all_statuses = sorted({ r.get("status","") for r in rows if isinstance(r, dict) } - {""})

# Filters
c1, c2, c3, c4 = st.columns([1.2,1.2,1.2,1.4])
with c1:
    sel_jobs = st.multiselect("Jobs", options=all_jobs, default=all_jobs)
with c2:
    sel_status = st.multiselect("Status", options=all_statuses, default=all_statuses)
with c3:
    date_from = st.date_input("From", value=(dt.date.today() - dt.timedelta(days=14)))
with c4:
    date_to = st.date_input("To", value=dt.date.today())

# Apply filters
rows_f = filter_jobs(rows, job_names=sel_jobs, statuses=sel_status, date_from=date_from, date_to=date_to)

# DataFrame
def _mk_df(rows):
    if not rows:
        return pd.DataFrame(columns=["ts","job","status","detail"])
    df = pd.DataFrame(rows)
    # stable columns
    for col in ["ts","job","status","detail"]:
        if col not in df.columns:
            df[col] = ""
    # sort newest first
    try:
        df["_ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("_ts", ascending=False).drop(columns=["_ts"])
    except Exception:
        pass
    return df[["ts","job","status","detail"]]

df = _mk_df(rows_f)

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric("Total runs", f"{len(rows_f):,}")
k2.metric("Successes", f"{sum(1 for r in rows_f if r.get('status')=='ok'): ,}")
k3.metric("Failures", f"{sum(1 for r in rows_f if r.get('status')=='error'): ,}")

st.divider()
st.subheader("Run History")
if df.empty:
    st.info("No job runs yet. Configure Cron Jobs or run helpers locally.")
else:
    st.dataframe(df, use_container_width=True)

    # Export
    st.divider()
    st.subheader("Export")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name=f"jobs_history_{dt.date.today().isoformat()}.csv", mime="text/csv")
