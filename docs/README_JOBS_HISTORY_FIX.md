# v7.6 — Jobs History fix

This patch adds `utils/jobs_history.py` with the functions the page expects:
- `read_jobs()`, `filter_jobs()`, `read_jobs_raw()`, `extract_error_snippet()`

It normalizes logs from `/data/logs` (preferred) or `/tmp/vega_data/logs` and
renders a simple Jobs History table with filters.

## Apply
1. Copy `utils/jobs_history.py` into `utils/`.
2. Replace `pages/48_Jobs_History.py` with the one in this zip (or keep yours if it imports the same helpers).
3. Deploy.
