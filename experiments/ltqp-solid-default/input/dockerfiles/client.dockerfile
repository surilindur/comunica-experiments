FROM comunica/query-sparql-link-traversal-solid:latest

ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT=120
ARG MAX_MEMORY=8192
ARG LOG_LEVEL=info
ARG COMUNICA_PORT=3000

ADD $CONFIG_CLIENT /tmp/engine.json

ENV COMUNICA_CONFIG /tmp/engine.json
ENV NODE_ENV production
ENV NODE_OPTIONS --max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT $QUERY_TIMEOUT
ENV LOG_LEVEL $LOG_LEVEL
ENV COMUNICA_PORT $COMUNICA_PORT

EXPOSE $COMUNICA_PORT

ENTRYPOINT [ "/bin/sh", "-c", "node ./bin/http.js --lenient --contextOverride --invalidateCache --idp void --context /tmp/context.json --port ${COMUNICA_PORT} --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
