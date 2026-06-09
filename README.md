# twingate-client-http-proxy — Twingate Userspace HTTP Proxy Docker Image

Built on `debian:bookworm-slim`, this image installs the official Twingate Linux client and runs it in **userspace HTTP Proxy mode** by default — no `NET_ADMIN`, `/dev/net/tun`, or service key required.

## Build

```bash
docker build -t twingate-client .
```

## Run

```bash
docker run -d --name twingate-client -p 9999:9999 twingate-client
```

## Management

All interactive management is done via `docker exec`:

```bash
# Setup runs automatically on first start — no manual steps needed

# Login
docker exec -it twingate-client twingate login

# Check status
docker exec -it twingate-client twingate status

# Logout
docker exec -it twingate-client twingate logout
```

## Using the Proxy

Once the container is running, any client configured to use an HTTP proxy can connect:

```bash
curl --proxy http://127.0.0.1:9999 https://example.com
```

## Persisting State (Optional)

To preserve login state across container rebuilds, use a named volume:

```bash
docker run -d --name twingate-client \
  -v twingate-state:/etc/twingate \
  -p 127.0.0.1:9999:9999 \
  twingate-client
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TWINGATE_HTTP_PROXY` | `0.0.0.0:9999` | HTTP proxy listen address |
| `TWINGATE_TUN` | `off` | TUN mode toggle (`on`/`off`) |
| `TWINGATE_RESTART_DELAY` | `5` | Seconds to wait before restarting the daemon |
| `TWINGATE_NETWORK` | `feedme` | Twingate network name (e.g. `acme` for `acme.twingate.com`) |
