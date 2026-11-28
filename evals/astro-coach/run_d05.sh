#!/bin/bash
cd /home/claude/harness-engineering/evals/astro-coach
for n in 1 2 3 4 5; do for c in bare harness; do
  [ -f "runs/d05-$c-r$n/status" ] && continue
  ./run_one.sh 05 "$c" "$n"
done; done
echo BATCH_DONE
