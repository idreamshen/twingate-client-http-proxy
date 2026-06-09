#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

/usr/local/bin/twingate-webui.py &
webui_pid=$!

while true; do
  /usr/sbin/twingated \
    --http-proxy "${TWINGATE_HTTP_PROXY}" \
    --tun "${TWINGATE_TUN}" &
  child="$!"

  trap 'kill -TERM "$child" "$webui_pid" 2>/dev/null || true; wait "$child" 2>/dev/null || true; exit 0' TERM INT

  wait "$child" || true
  sleep "${TWINGATE_RESTART_DELAY}"
done
