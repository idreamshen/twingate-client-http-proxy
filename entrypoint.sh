#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

if [ ! -f /etc/twingate/.setup-done ]; then
  printf 'A\n%s\nn\nn\nn\nn\n' "${TWINGATE_NETWORK}" | twingate setup
  touch /etc/twingate/.setup-done
fi

while true; do
  /usr/sbin/twingated \
    --http-proxy "${TWINGATE_HTTP_PROXY}" \
    --tun "${TWINGATE_TUN}" &
  child="$!"

  trap 'kill -TERM "$child" 2>/dev/null || true; wait "$child" 2>/dev/null || true; exit 0' TERM INT

  wait "$child" || true
  sleep "${TWINGATE_RESTART_DELAY}"
done
