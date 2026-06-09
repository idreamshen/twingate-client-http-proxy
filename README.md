# twingate-client-http-proxy — Twingate Userspace HTTP Proxy Docker Image

基于 `debian:bookworm-slim`，安装官方 Twingate Linux 客户端，默认以 **userspace HTTP Proxy 模式**运行，不需要 `NET_ADMIN`、`/dev/net/tun` 或 service key。

## 构建

```bash
docker build -t twingate-client .
```

## 启动

```bash
docker run -d --name twingate-client -p 9999:9999 twingate-client
```

## 管理

所有交互式管理通过 `docker exec` 完成：

```bash
# 首次启动时自动完成 setup，无需手动操作

# 登录
docker exec -it twingate-client twingate login

# 查看状态
docker exec -it twingate-client twingate status

# 登出
docker exec -it twingate-client twingate logout
```

## 使用代理

容器启动后，任何显式配置了 HTTP proxy 的客户端即可使用：

```bash
curl --proxy http://127.0.0.1:9999 https://example.com
```

## 保留状态（可选）

容器删除后重建时，如果希望保留登录状态，使用命名 volume：

```bash
docker run -d --name twingate-client \
  -v twingate-state:/etc/twingate \
  -p 127.0.0.1:9999:9999 \
  twingate-client
```

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TWINGATE_HTTP_PROXY` | `0.0.0.0:9999` | HTTP proxy 监听地址 |
| `TWINGATE_TUN` | `off` | TUN 模式开关（`on`/`off`） |
| `TWINGATE_RESTART_DELAY` | `5` | daemon 重启前等待秒数 |
| `TWINGATE_NETWORK` | `feedme` | Twingate 网络名称（如 `acme` 对应 `acme.twingate.com`） |
