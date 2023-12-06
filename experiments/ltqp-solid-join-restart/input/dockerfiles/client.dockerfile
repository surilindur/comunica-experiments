# syntax=docker/dockerfile:1

FROM bitnami/git:latest AS git

RUN git clone --depth 1 --branch main --single-branch https://github.com/surilindur/comunica-components.git /opt/client

WORKDIR /opt/client

RUN git checkout 2611b3fed112c720ed9b708e8bd79a74f150cf2f

FROM node:21.4.0

COPY --from=git /opt/client /opt/client

WORKDIR /opt/client

RUN corepack enable && yarn install --immutable && yarn build

WORKDIR /opt/client/engines/query-sparql-components

ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT
ARG MAX_MEMORY
ARG LOG_LEVEL

ADD $CONFIG_CLIENT /tmp/engine.json

ENV COMUNICA_CONFIG /tmp/engine.json
ENV NODE_ENV production
ENV NODE_OPTIONS --max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT $QUERY_TIMEOUT
ENV LOG_LEVEL $LOG_LEVEL

EXPOSE 3000

ENTRYPOINT []
CMD [ "/bin/sh", "-c", "node ./bin/http.js --lenient --contextOverride --invalidateCache --workers 1 --context /tmp/context.json --port 3000 --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
