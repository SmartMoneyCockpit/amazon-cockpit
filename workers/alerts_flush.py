"""
Flush alerts: if new vs last fingerprint, send email/webhook and log to jobs history.
Safe to run on cron.
"""
from __future__ import annotations
from utils.alerts_notify import notify_if_new
from utils.jobs_history import write_job

def main():
    res = notify_if_new(subject_prefix="Vega Alerts Update")
    status = res.get("status","ok")
    write_job(job="alerts_flush", status=status, details=res)

if __name__ == "__main__":
    main()
