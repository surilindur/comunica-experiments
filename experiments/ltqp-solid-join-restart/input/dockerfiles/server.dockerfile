FROM solidproject/community-server:7.0.1

ARG CONFIG_SERVER
ARG LOG_LEVEL
ARG BASE_URL

ADD $CONFIG_SERVER /tmp/config.json

ENV LOG_LEVEL $LOG_LEVEL
ENV BASE_URL $BASE_URL
ENV NODE_OPTIONS --max-old-space-size=8192

ENTRYPOINT []
CMD [ "/bin/sh", "-c", "node bin/server.js --config /tmp/config.json --loggingLevel ${LOG_LEVEL} --baseUrl ${BASE_URL} --rootFilePath /data" ]
