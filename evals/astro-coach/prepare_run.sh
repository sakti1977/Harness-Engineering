#!/bin/sh
# Build one agent workspace for an astro-coach eval run. See RUN_POLICY.md.
# Usage: prepare_run.sh <product-git-dir> <defect: 01|02|03|none> <out-dir>
# The workspace has the product at the pinned commit, the defect patch applied,
# and a fresh single-commit history, so the fixing commits are not reachable.
set -eu
PRODUCT_GIT="$1"; DEFECT="$2"; OUT="$3"
PIN=43c695a
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -e "$OUT" ] && { echo "refusing to overwrite $OUT" >&2; exit 1; }
mkdir -p "$OUT"
# Whole repository, not just the app: the product tests read files at the repo root.
git -C "$PRODUCT_GIT" archive "$PIN" | tar -x -C "$OUT"
cd "$OUT"
if [ "$DEFECT" != "none" ]; then
  PATCH="$(ls "$HERE"/defects/"$DEFECT"-*.patch)"
  git apply "$PATCH"
fi
# Fresh history: the agent sees one commit and no fixing commits.
git init -q
git add -A
git -c user.name=eval -c user.email=eval@localhost commit -q -m "pinned snapshot $PIN with defect $DEFECT"
cp "$HERE"/reports/"$DEFECT"-*.md "$OUT/" 2>/dev/null || true
echo "workspace: $OUT"
echo "commits: $(git rev-list --count HEAD)"
echo "tree hash: $(git rev-parse HEAD^{tree})"
