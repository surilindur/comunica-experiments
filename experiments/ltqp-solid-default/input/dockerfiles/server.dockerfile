FROM solidproject/community-server:edge

ARG CONFIG_SERVER
ARG LOG_LEVEL
ARG BASE_URL

ADD $CONFIG_SERVER /tmp/config.json

ENV NODE_ENV=production

ENV CSS_CONFIG=/tmp/config.json
ENV CSS_LOGGING_LEVEL=$LOG_LEVEL
ENV CSS_BASE_URL=$BASE_URL
ENV CSS_ROOT_FILE_PATH=/data

ENTRYPOINT [ "node", "bin/server.js" ]
