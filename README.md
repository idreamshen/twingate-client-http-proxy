# twingate-client-http-proxy — Twingate Userspace HTTP Proxy Docker Image

Built on `debian:bookworm-slim`, this image installs the official Twingate Linux client and runs it in **userspace HTTP Proxy mode** by default — no `NET_ADMIN`, `/dev/net/tun`, or service key required.

It also includes a built-in **Web UI** (port `8080`) to configure the Twingate network, run login, and view status — no `docker exec` needed.

## Build

```bash
docker build -t twingate-client-http-proxy .
```

## Run

```bash
docker run -d --name twingate-client-http-proxy \
  -p 9999:9999 \
  -p 8080:8080 \
  twingate-client-http-proxy
```

## Usage

### Web UI (recommended)

Open http://127.0.0.1:8080 in your browser.

1. Enter your **Twingate network name** (e.g. `acme` for `acme.twingate.com`).
2. Click **Login** — this runs `twingate setup` and `twingate start` automatically.
3. The **Status** area polls automatically every 2 seconds and refreshes with `twingate status` output (including any authentication URL).

### CLI (alternative)

```bash
# Setup (network name required)
docker exec -it twingate-client-http-proxy twingate setup

# Start (login)
docker exec -it twingate-client-http-proxy twingate start

# Check status
docker exec -it twingate-client-http-proxy twingate status

# Stop (logout)
docker exec -it twingate-client-http-proxy twingate stop
```

## Using the Proxy

Once the container is running, any client configured to use an HTTP proxy can connect:

```bash
curl --proxy http://127.0.0.1:9999 https://example.com
```

## Persisting State (Optional)

To preserve login state and network configuration across container rebuilds, use a named volume:

```bash
docker run -d --name twingate-client-http-proxy \
  -v twingate-state:/etc/twingate \
  -p 127.0.0.1:9999:9999 \
  -p 127.0.0.1:8080:8080 \
  twingate-client-http-proxy
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TWINGATE_HTTP_PROXY` | `0.0.0.0:9999` | HTTP proxy listen address |
| `TWINGATE_TUN` | `off` | TUN mode toggle (`on`/`off`) |
| `TWINGATE_RESTART_DELAY` | `5` | Seconds to wait before restarting the daemon |
| `WEBUI_ADDR` | `0.0.0.0:8080` | Web UI listen address |
