#!/usr/bin/env bash
set -euo pipefail
BRANCH="bundle-14-105-render-handoff-20251008"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Run this script inside your repo root."; exit 1; }
git checkout -b "$BRANCH"
mkdir -p ops .github
cp -f DEPLOY_ON_RENDER.md ./
cp -f render.yaml ./
cp -f RENDER_JOBS.md ./
cp -f OPS_TICKET_TEMPLATE.md ./
cp -f ops/render_jobs_example.json ./ops/ || true
cp -f .github/PULL_REQUEST_TEMPLATE.md ./.github/ || true
cp -f GITIGNORE_RECOMMENDED.txt ./
if ! grep -q "backups/" .gitignore 2>/dev/null; then
  cat GITIGNORE_RECOMMENDED.txt >> .gitignore || true
fi
git add -A
git commit -F PR_COMMIT_MESSAGE.txt
git push -u origin "$BRANCH"
