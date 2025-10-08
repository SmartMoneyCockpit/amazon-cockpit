#!/usr/bin/env bash
set -euo pipefail
BRANCH="bundle-14-105-render-handoff-20251008"

# Ensure we're at repo root
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Run this script inside your repo root."; exit 1; }

# Create branch
git checkout -b "$BRANCH"

# Copy docs into repo
mkdir -p ops .github
cp -f DEPLOY_ON_RENDER.md ./
cp -f render.yaml ./
cp -f RENDER_JOBS.md ./
cp -f ops/render_jobs_example.json ./ops/ || true
cp -f .github/PULL_REQUEST_TEMPLATE.md ./.github/ || true
cp -f GITIGNORE_RECOMMENDED.txt ./

# Merge .gitignore suggestion (only if not present)
if ! grep -q "backups/" .gitignore 2>/dev/null; then
  cat GITIGNORE_RECOMMENDED.txt >> .gitignore || true
fi

git add -A
git commit -F PR_COMMIT_MESSAGE.txt

# Push and print PR URL
git push -u origin "$BRANCH"

REMOTE_URL="$(git config --get remote.origin.url)"
# Normalize to https PR URL
if [[ "$REMOTE_URL" =~ ^git@github.com:(.*)/(.*)\.git$ ]]; then
  OWNER="${BASH_REMATCH[1]}"; REPO="${BASH_REMATCH[2]}"
  echo "Open PR: https://github.com/$OWNER/$REPO/compare/$BRANCH?expand=1"
elif [[ "$REMOTE_URL" =~ ^https://github.com/(.*)/(.*)\.git$ ]]; then
  OWNER="${BASH_REMATCH[1]}"; REPO="${BASH_REMATCH[2]}"
  echo "Open PR: https://github.com/$OWNER/$REPO/compare/$BRANCH?expand=1"
else
  echo "Push succeeded. Open your repo and create a PR from branch $BRANCH"
fi
