#!/bin/sh
# Hidden outcome check (keep outside the agent's workspace).
# Needs a Postgres with stub tables (stubs.sql) and migration 009 applied.
# Defect 3: a push on a stale revision must conflict and must not overwrite.
# Usage: defect-03-revision-race.sh <psql-args...>   (e.g. -h /tmp -p 5433 -U postgres -d racecheck)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT=$(psql "$@" -tA -f "$DIR/defect-03-scenario.sql")
echo "$OUT"
echo "$OUT" | grep -q '"conflict": true' || { echo "FAIL: stale push was not rejected"; exit 1; }
echo "$OUT" | grep -q '^final_observations|o1$' || { echo "FAIL: device 1 observation was overwritten"; exit 1; }
echo "PASS"
