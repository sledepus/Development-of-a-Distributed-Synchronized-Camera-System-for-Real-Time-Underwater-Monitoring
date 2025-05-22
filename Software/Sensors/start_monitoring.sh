#!/usr/bin/env bash
set -Eeuo pipefail

cd ~/Bachelor/sensors || exit 1
source ~/Bachelor/gpio/bin/activate

# Starting sensor script as a service running in the background
python3 start_sensors.py &
SENSOR_PID=$!
echo "sensors started (pid $SENSOR_PID)"

# Kill service running sensor script when exiting
cleanup() {
  echo "Stopping sensor_board_http.py (pid $SENSOR_PID)…"
  kill "$SENSOR_PID" 2>/dev/null || true
  wait  "$SENSOR_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# run web server in foreground
echo "Starting dashboard"
python3 dashboard.py
