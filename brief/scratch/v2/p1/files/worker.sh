#!/usr/bin/env bash
# worker.sh: a pretend background worker for Day 6.
# Every 2 seconds it "processes" one job and prints a line.
# On SIGTERM it finishes the job it is on, then exits cleanly with code 0.
# SIGKILL cannot be caught, so with kill -9 it stops at once, mid-job.

job=0
stop=0

# on_term runs when SIGTERM arrives. shellcheck cannot see that, so we tell it.
# shellcheck disable=SC2317
on_term() {
  echo "worker: got SIGTERM, finishing job $job, then exiting"
  stop=1
}
# trap: when SIGTERM arrives, run on_term instead of dying at once.
trap on_term TERM

echo "worker: started with PID $$"
while [ "$stop" -eq 0 ]; do
  job=$((job + 1))
  echo "worker: processing job $job"
  sleep 2
done
echo "worker: stopped cleanly after job $job"
exit 0
