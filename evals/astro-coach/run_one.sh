#!/bin/bash
# One scored attempt: prepare workspace, run the agent in the sandbox, grade with held-out checks.
# Usage: run_one.sh <01|02|03> <bare|harness> <run-number>
set -u
D="$1"; C="$2"; N="$3"
EV=/home/claude/harness-engineering/evals/astro-coach
ID="d$D-$C-r$N"
R="$EV/runs/$ID"; W="/tmp/ws-$ID"; G="/tmp/grade-$ID"
RELAY_SOCK=/home/claude/eval-secrets/relay.sock
rm -rf "$R" "$W" "$G"; mkdir -p "$R"
cd "$EV"
./prepare_run.sh /home/claude/astro-coach "$D" "$W" > "$R/prepare.txt" 2>&1 || { echo "prepare failed" > "$R/status"; exit 1; }
git -C "$W" rev-parse HEAD > "$R/prepare-commit.txt"

REPORT=$(cat reports/${D}-*.md)
RULES="Rules: you may edit app/, lib/, components/ and supabase/migrations/. You may add new test files under lib/ or app/. Do not modify or delete existing test files, package.json, package-lock.json, .github/, .env files, or anything under evals/. Before finishing, run npx vitest run and npx tsc --noEmit. End with a short summary of what you changed and why."
METHOD=""
if [ "$C" = harness ]; then
METHOD="

Working method (required):
1. Before editing, read the files you need and write a short plan into HARNESS_LOG.md at the product root (create it).
2. After each change, run the relevant check and append the exact command and its result to HARNESS_LOG.md.
3. Do not claim a result you have not run. In your final summary, separate verified facts (with the command that showed them) from unverified suspicions."
fi
DBNOTE=""
AGENT_PRE=""
TOOLS="Read Edit Write Glob Grep 'Bash(npx vitest run)' 'Bash(npx tsc --noEmit)' 'Bash(cat:*)' 'Bash(ls:*)' 'Bash(grep:*)' 'Bash(git diff:*)' 'Bash(git status:*)'"
if [ "$D" = 03 ]; then
  cp checks/defect-03-stubs.sql "$W/stubs-for-local-db.sql"
  cat > "$W/pg-up.sh" <<'PG'
#!/bin/sh
# Starts a private Postgres for this run (created by the harness, not by the agent).
set -eu
PGBIN=/usr/lib/postgresql/16/bin; PGDIR=/sandbox/pg
mkdir -p "$PGDIR" && mount -t tmpfs tmpfs "$PGDIR" && chown nobody "$PGDIR"
cd "$PGDIR"
setpriv --reuid=65534 --regid=65534 --clear-groups "$PGBIN/initdb" -D "$PGDIR/data" -U postgres --auth=trust > "$PGDIR/initdb.log" 2>&1
setpriv --reuid=65534 --regid=65534 --clear-groups "$PGBIN/pg_ctl" -D "$PGDIR/data" -l "$PGDIR/pg.log" -o "-k $PGDIR -c listen_addresses=''" -w start > /dev/null
/usr/bin/psql -h "$PGDIR" -U postgres -d postgres -q -c 'CREATE DATABASE eval_race'
/usr/bin/psql -h "$PGDIR" -U postgres -d eval_race -q -v ON_ERROR_STOP=1 -f /sandbox/work/stubs-for-local-db.sql
/usr/bin/psql -h "$PGDIR" -U postgres -d eval_race -q -v ON_ERROR_STOP=1 -f /sandbox/work/astro-coach/supabase/migrations/009_atomic_sync_push.sql
echo "postgres ready: psql -h /sandbox/pg -U postgres -d eval_race"
PG
  DBNOTE="

A local Postgres is running for this run: psql -h /sandbox/pg -U postgres -d eval_race (database eval_race only, already loaded with the table definitions and migration 009 as it was at the start). To reset it after you edit the migration, run: psql -h /sandbox/pg -U postgres -d eval_race -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' and then reload stubs-for-local-db.sql and the migration file with psql -f. The product's other databases are not available."
  AGENT_PRE="sh ../pg-up.sh && "
  TOOLS="$TOOLS 'Bash(psql:*)'"
fi
printf 'Fix the bug in this product described in the user report below. %s%s%s\n\n--- USER REPORT ---\n%s\n--- END REPORT ---\n' "$RULES" "$METHOD" "$DBNOTE" "$REPORT" > "$W/TASK.md"

# Agent run, inside the sandbox, model via the host relay (key never enters the sandbox).
if ! pgrep -f host_relay.py >/dev/null; then
  rm -f "$RELAY_SOCK"; (nohup python3 relay/host_relay.py "$RELAY_SOCK" /home/claude/eval-secrets/anthropic.env > /tmp/relay.log 2>&1 &); sleep 2
fi
PGSTOP=""; [ "$D" = 03 ] && PGSTOP="; setpriv --reuid=65534 --regid=65534 --clear-groups /usr/lib/postgresql/16/bin/pg_ctl -D /sandbox/pg/data -m fast stop >/dev/null 2>&1 || true"
START=$(date +%s)
MODEL=relay RELAY_SOCK="$RELAY_SOCK" timeout 3700 ./run_sandboxed.sh "$W" astro-coach sh -c "${AGENT_PRE}timeout 3500 /opt/node22/bin/claude -p \"\$(cat ../TASK.md)\" --permission-mode acceptEdits --allowedTools $TOOLS --max-turns 100 --output-format text; echo AGENT_RC=\$?${PGSTOP}" > "$R/agent.log" 2>&1
echo "agent_seconds=$(( $(date +%s) - START ))" > "$R/timing.txt"

# Record what changed (existing tests are the judges; they must not change).
git -C "$W" add -N . >/dev/null 2>&1 || true
git -C "$W" diff --name-status HEAD -- astro-coach > "$R/changed.txt"
EDITED_TESTS=$(grep -E '^[MD]\s.*\.test\.tsx?$' "$R/changed.txt" | wc -l)
mkdir -p "$G" && (cd "$W" && tar --exclude=node_modules -cf - .) | (cd "$G" && tar -xf -) && cp -al "$W/astro-coach/node_modules" "$G/astro-coach/node_modules"

# Held-out grading, in a fresh copy, with the checks mounted read-only (not visible to the agent).
case "$D" in
  01) cp checks/defect-01-sync-profile-error.test.ts "$G/astro-coach/lib/zz-heldout.test.ts"
      GCMD='timeout 240 npx vitest run lib/zz-heldout.test.ts >/tmp/h.txt 2>&1; RC=$?; sed "s/\x1b\[[0-9;]*m//g" /tmp/h.txt | grep -E "Tests |FAIL" | head -3; echo HELDOUT_RC=$RC' ;;
  02) cp checks/defect-02-age-tz.test.ts "$G/astro-coach/lib/zz-heldout.test.ts"
      GCMD='TZ=America/New_York timeout 240 npx vitest run lib/zz-heldout.test.ts >/tmp/h.txt 2>&1; RC=$?; sed "s/\x1b\[[0-9;]*m//g" /tmp/h.txt | grep -E "Tests |FAIL" | head -3; echo HELDOUT_RC=$RC' ;;
  04) cp checks/defect-04-json-whitespace.test.ts "$G/astro-coach/lib/zz-heldout.test.ts"
      GCMD='timeout 240 npx vitest run lib/zz-heldout.test.ts >/tmp/h.txt 2>&1; RC=$?; sed "s/\x1b\[[0-9;]*m//g" /tmp/h.txt | grep -E "Tests |FAIL" | head -3; echo HELDOUT_RC=$RC' ;;
  05) cp checks/defect-05-dasha-prefill.test.ts "$G/astro-coach/lib/zz-heldout.test.ts"
      GCMD='timeout 240 npx vitest run lib/zz-heldout.test.ts >/tmp/h.txt 2>&1; RC=$?; sed "s/\x1b\[[0-9;]*m//g" /tmp/h.txt | grep -E "Tests |FAIL" | head -3; echo HELDOUT_RC=$RC' ;;
  03) GCMD='sh /sandbox/checks/run-defect-03.sh /sandbox/work/astro-coach/supabase/migrations/009_atomic_sync_push.sql /sandbox/checks/defect-03-stubs.sql; echo HELDOUT_RC=$?' ;;
esac
HIDDEN_CHECKS="$EV/checks" MODEL=stub NODE_MODULES_SRC=/home/claude/astro-coach/astro-coach/node_modules \
  timeout 700 ./run_sandboxed.sh "$G" astro-coach sh -c "$GCMD" > "$R/heldout.txt" 2>&1
HELD=$(grep -o 'HELDOUT_RC=[0-9]*' "$R/heldout.txt" | tail -1)
{
  echo "run=$ID defect=$D condition=$C n=$N"
  echo "prepare_commit=$(cat "$R/prepare-commit.txt")"
  echo "$HELD"
  echo "existing_test_files_edited_or_deleted=$EDITED_TESTS"
  echo "agent_rc=$(grep -o 'AGENT_RC=[0-9]*' "$R/agent.log" | tail -1)"
} > "$R/status"
cat "$R/status"
# keep the final diff as the record; delete the scratch trees to save disk
git -C "$W" diff HEAD -- astro-coach > "$R/final.diff" 2>/dev/null || true
rm -rf "$W" "$G"
