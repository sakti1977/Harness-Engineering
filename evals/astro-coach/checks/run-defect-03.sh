#!/bin/sh
# Hidden check for defect 3, run INSIDE the sandbox (see run_sandboxed.sh).
# Args: <migration.sql> <stubs.sql>; runs as root except postgres itself (which refuses root).
set -eu
MIG="$1"; STUBS="$2"; CHK=/sandbox/checks
PGBIN=/usr/lib/postgresql/16/bin
PGDIR=/sandbox/pg
mkdir -p "$PGDIR" && mount -t tmpfs tmpfs "$PGDIR"
chown nobody "$PGDIR"
cd "$PGDIR"
setpriv --reuid=65534 --regid=65534 --clear-groups "$PGBIN/initdb" -D "$PGDIR/data" -U postgres --auth=trust >/sandbox/initdb.log 2>&1
stop_pg() { setpriv --reuid=65534 --regid=65534 --clear-groups "$PGBIN/pg_ctl" -D "$PGDIR/data" -m fast stop >/dev/null 2>&1 || true; }
trap stop_pg EXIT
setpriv --reuid=65534 --regid=65534 --clear-groups "$PGBIN/pg_ctl" -D "$PGDIR/data" -l "$PGDIR/pg.log" \
  -o "-k $PGDIR -c listen_addresses=''" -w start >/dev/null
/usr/bin/psql -h "$PGDIR" -U postgres -d postgres -q -c 'CREATE DATABASE racecheck' 
PSQL="/usr/bin/psql -h $PGDIR -U postgres -d racecheck -q -v ON_ERROR_STOP=1"
$PSQL -f "$STUBS"
$PSQL -f "$MIG"
rc=0
sh "$CHK/defect-03-revision-race.sh" -h "$PGDIR" -p 5432 -U postgres -d racecheck || rc=$?
exit "$rc"
