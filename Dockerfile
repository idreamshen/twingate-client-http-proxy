FROM debian:bookworm-slim

ENV TWINGATE_HTTP_PROXY=0.0.0.0:9999
ENV TWINGATE_TUN=off
ENV TWINGATE_RESTART_DELAY=5
ENV TWINGATE_NETWORK=feedme

RUN apt-get update -qq \
  && apt-get install -y -qq --no-install-recommends curl gnupg2 ca-certificates \
  && curl -fsSL https://packages.twingate.com/apt/gpg.key | gpg --batch --no-tty --dearmor -o /usr/share/keyrings/twingate-client-keyring.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/twingate-client-keyring.gpg] https://packages.twingate.com/apt/ * *" > /etc/apt/sources.list.d/twingate.list \
  && apt-get update -qq \
  && apt-get install -y -qq --no-install-recommends twingate \
  && apt-get purge -y -qq gnupg2 \
  && apt-get autoremove -y -qq \
  && rm -rf /var/lib/apt/lists/*

RUN printf '#!/bin/sh\nexit 0\n' > /usr/bin/systemctl && chmod +x /usr/bin/systemctl

COPY entrypoint.sh /usr/local/bin/twingate-userspace-entrypoint
RUN chmod +x /usr/local/bin/twingate-userspace-entrypoint

EXPOSE 9999

ENTRYPOINT ["/usr/local/bin/twingate-userspace-entrypoint"]
