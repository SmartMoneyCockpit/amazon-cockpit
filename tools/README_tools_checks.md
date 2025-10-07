# Jobs YAML — minimal schema checks

Each item in `tools/*.yaml` should include:
- `name`: A short name for the job.
- `schedule`: Cron-like or human-readable time descriptor your runner expects.
- `task`: The task id/name your worker understands.

Example (list form):
```yaml
- name: daily_snapshot
  schedule: "0 7 * * *"
  task: "snapshot:daily"
- name: digest
  schedule: "30 12 * * 1-5"
  task: "digest:run"
```

Use `utils/cron_validate.validate_all()` to scan and list problems before enabling jobs.
