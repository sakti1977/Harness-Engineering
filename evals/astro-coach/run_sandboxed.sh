#!/bin/sh
# Run one command for an astro-coach eval inside a sandbox. See RUN_POLICY.md.
# Usage: [HIDDEN_CHECKS=<dir>] [MODEL=stub|relay] [RELAY_SOCK=<socket>] run_sandboxed.sh <workspace-root> <product-subdir> <command...>
#   workspace-root is the whole repo workspace (the tests read files at the repo root);
#   product-subdir is where the command runs, e.g. astro-coach.
#   - no network except loopback (new network namespace)
#   - home, root, mnt, srv, tmp are private tmpfs; everything else on the host is hidden or read-only
#   - the workspace is the only writable tree
#   - MODEL=stub: the fixed-reply Anthropic stub on 127.0.0.1:8787
#   - MODEL=relay: the host relay (RELAY_SOCK) on 127.0.0.1:8788; the API key stays on the host
#   - environment is cleared; no API keys enter the sandbox
# Needs root (unshare). Does not replace a container; it is the strongest isolation available here.
set -eu
WS="$(cd "$1" && pwd)"; SUB="$2"; shift 2
HERE="$(cd "$(dirname "$0")" && pwd)"
MODEL="${MODEL:-stub}"
RELAY="${RELAY_SOCK:-}"
if [ "$MODEL" = relay ] && [ -z "$RELAY" ]; then echo "MODEL=relay needs RELAY_SOCK" >&2; exit 2; fi
NM_SRC="${NODE_MODULES_SRC:-/home/claude/astro-coach/astro-coach/node_modules}"
if [ ! -e "$WS/$SUB/node_modules" ] && [ -d "$NM_SRC" ]; then
  cp -al "$NM_SRC" "$WS/$SUB/node_modules"   # hard links: no network, no copy of the bytes
fi
# Arguments for the inner shell are passed as positional parameters, not interpolated.
exec unshare --net --mount --fork sh -c '
  set -eu
  WS="$1"; STUB="$2"; LOUP="$3"; SUB="$4"; CHK="$5"; MODEL="$6"; RELAY="$7"; PIPE="$8"; shift 8
  python3 "$LOUP"
  mount --make-rprivate /
  mkdir -p /sandbox/work /sandbox/stub /sandbox/home /sandbox/checks
  mount --bind "$WS" /sandbox/work
  mount --bind "$STUB" /sandbox/stub/anthropic_stub.py 2>/dev/null || { : > /sandbox/stub/anthropic_stub.py; mount --bind "$STUB" /sandbox/stub/anthropic_stub.py; }
  mount --bind "$PIPE" /sandbox/stub/sandbox_pipe.py 2>/dev/null || { : > /sandbox/stub/sandbox_pipe.py; mount --bind "$PIPE" /sandbox/stub/sandbox_pipe.py; }
  if [ -n "$CHK" ]; then   # hidden checks: read-only, outside the writable workspace
    mount --bind "$CHK" /sandbox/checks && mount -o remount,bind,ro /sandbox/checks
  fi
  if [ "$MODEL" = relay ]; then
    : > /sandbox/relay.sock && mount --bind "$RELAY" /sandbox/relay.sock
    python3 /sandbox/stub/sandbox_pipe.py /sandbox/relay.sock 8788 2>/sandbox/pipe.log &
    SERVICE_PID=$!
    BASE=http://127.0.0.1:8788
  else
    python3 /sandbox/stub/anthropic_stub.py 8787 2>/sandbox/stub.log &
    SERVICE_PID=$!
    BASE=http://127.0.0.1:8787
  fi
  for d in /home /root /mnt /srv /tmp; do
    [ -d "$d" ] && mount -t tmpfs tmpfs "$d"
  done
  mkdir -p /home/sandbox
  sleep 1
  cd "/sandbox/work/$SUB"
  rc=0
  env -i PATH="$PATH" HOME=/home/sandbox LANG=C.UTF-8 TMPDIR=/tmp \
    ANTHROPIC_BASE_URL="$BASE" ANTHROPIC_API_KEY=relay-injected SANDBOX=1 "$@" || rc=$?
  kill "$SERVICE_PID" 2>/dev/null || true
  exit "$rc"
' sandbox "$WS" "$HERE/stubs/anthropic_stub.py" "$HERE/stubs/lo_up.py" "$SUB" "${HIDDEN_CHECKS:-}" "$MODEL" "$RELAY" "$HERE/relay/sandbox_pipe.py" "$@"
