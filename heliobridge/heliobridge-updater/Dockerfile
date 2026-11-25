FROM ghcr.io/home-assistant/amd64-base:latest
RUN apk add --no-cache bash curl jq
COPY run.sh /run.sh
RUN chmod 0755 /run.sh
CMD ["/run.sh"]
