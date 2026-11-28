#!/bin/bash
# Runs the full matrix: 3 defects x 2 conditions x 5 repeats, interleaved by repeat.
cd /home/claude/harness-engineering/evals/astro-coach
for n in 1 2 3 4 5; do for d in 01 02 03 04; do for c in bare harness; do
  id="d$d-$c-r$n"
  [ -f "runs/$id/status" ] && continue
  ./run_one.sh "$d" "$c" "$n"
done; done; done
echo BATCH_DONE
