# Twingate Client Http Proxy

Userspace HTTP Proxy Docker image for the official Twingate Linux client — no `NET_ADMIN`, `/dev/net/tun`, or service key required. Includes a built-in Web UI (port `8080`) for configuration and status.

[![Build and Push Docker Image](https://github.com/idreamshen/twingate-client-http-proxy/actions/workflows/docker-image.yml/badge.svg)](https://github.com/idreamshen/twingate-client-http-proxy/actions/workflows/docker-image.yml)

## User Guide

### Pull & Run

```bash
docker pull ghcr.io/idreamshen/twingate-client-http-proxy:latest

docker run -d --name twingate-client-http-proxy \
  -p 127.0.0.1:9999:9999 \
  -p 127.0.0.1:8080:8080 \
  ghcr.io/idreamshen/twingate-client-http-proxy:latest
```

### Web UI (recommended)

Open http://127.0.0.1:8080 in your browser.

1. Enter your **Twingate network name** (e.g. `acme` for `acme.twingate.com`).
2. Click **Login** — this runs `twingate setup` and `twingate start` automatically.
3. The **Status** and **Resources** areas poll automatically every 2 seconds, showing `twingate status` and `twingate resources` output.

### CLI (alternative)

```bash
# Setup (network name required)
docker exec -it twingate-client-http-proxy twingate setup

# Start (login)
docker exec -it twingate-client-http-proxy twingate start

# Check status
docker exec -it twingate-client-http-proxy twingate status

# List resources
docker exec -it twingate-client-http-proxy twingate resources

# Stop (logout)
docker exec -it twingate-client-http-proxy twingate stop
```

### Using the Proxy

Once the container is running, any client configured to use an HTTP proxy can connect:

```bash
curl --proxy http://127.0.0.1:9999 https://example.com
```

### Persisting State (Optional)

To preserve login state and network configuration across container rebuilds, use a named volume:

```bash
docker run -d --name twingate-client-http-proxy \
  -v twingate-state:/etc/twingate \
  -p 127.0.0.1:9999:9999 \
  -p 127.0.0.1:8080:8080 \
  ghcr.io/idreamshen/twingate-client-http-proxy:latest
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TWINGATE_HTTP_PROXY` | `0.0.0.0:9999` | HTTP proxy listen address |
| `TWINGATE_TUN` | `off` | TUN mode toggle (`on`/`off`) |
| `TWINGATE_RESTART_DELAY` | `5` | Seconds to wait before restarting the daemon |
| `WEBUI_ADDR` | `0.0.0.0:8080` | Web UI listen address |

## Development Guide

### Build Locally

```bash
docker build -t twingate-client-http-proxy .
```

### CI (GitHub Actions)

On every push to `main` or a `v*` tag, GitHub Actions automatically builds the image and pushes it to GitHub Container Registry:

```bash
docker pull ghcr.io/idreamshen/twingate-client-http-proxy:latest
```
