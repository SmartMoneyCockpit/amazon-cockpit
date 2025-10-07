"""
Write a simple heartbeat snapshot (env/dirs/python) to snapshots/. Safe to run hourly/daily.
"""
from __future__ import annotations
from utils.sentinel import check_python, check_dirs, check_env
from utils.snapshot_export import save_csv

def main():
    env = check_env(["SENDGRID_API_KEY","EMAIL_FROM","EMAIL_TO","WEBHOOK_URL"])
    dirs = check_dirs()
    py = check_python()
    rows = []
    rows.extend([{"section":"python","key":k,"value":v} for k,v in py.items()])
    rows.extend([{"section":"dirs","key":k,"value":v} for k,v in dirs.items()])
    rows.extend([{"section":"env","key":k,"value":v} for k,v in env.items()])
    path = save_csv(rows, "heartbeat")
    return path

if __name__ == "__main__":
    main()
