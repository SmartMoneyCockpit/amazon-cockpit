## Summary
Docs-only PR: Render deployment handoff + Render Jobs schedules (UTC).

## What changed
- DEPLOY_ON_RENDER.md
- render.yaml
- RENDER_JOBS.md
- ops/render_jobs_example.json
- GITIGNORE_RECOMMENDED.txt

## Verification
- Open Utilities → Developer Tools → Run All Smoke Tests
- (Optional) Create demo data → validate Daily Digest, Alerts, Backups, Inventory, Jobs

## Checklist
- [ ] Secrets set in Render
- [ ] Web service deployed and reachable
- [ ] Jobs created with UTC schedules
- [ ] Digest disabled marker honored if toggled
