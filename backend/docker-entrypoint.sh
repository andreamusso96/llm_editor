#!/usr/bin/env sh
set -e

STATE_FILE=/var/lib/app/.init_done
mkdir -p "$(dirname "$STATE_FILE")"

if [ ! -f "$STATE_FILE" ]; then
  echo "[entrypoint] first boot: running init"
  python /app/init.py
  # write a timestamp so we can log when init happened
  date > "$STATE_FILE"
else
  echo "[entrypoint] init already done on $(cat "$STATE_FILE"), skipping"
fi

# Hand off to the main process (PID 1)
exec "$@"
