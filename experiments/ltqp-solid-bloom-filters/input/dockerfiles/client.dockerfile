# syntax=docker/dockerfile:1

FROM bitnami/git:latest AS git

RUN git clone --branch main --single-branch https://github.com/surilindur/comunica-components.git /opt/client

WORKDIR /opt/client

RUN git checkout e9e596effba646e36ae1a5e592eca1a07749a033

FROM node:21.6-slim

COPY --from=git /opt/client /opt/client

WORKDIR /opt/client

RUN corepack enable && yarn install --immutable && yarn build

WORKDIR /opt/client/engines/query-sparql-components

ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT=120
ARG MAX_MEMORY=8192
ARG LOG_LEVEL=info
ARG COMUNICA_PORT=3000
ARG COMUNICA_WORKERS=1

ADD $CONFIG_CLIENT /tmp/engine.json

ENV COMUNICA_CONFIG /tmp/engine.json
ENV NODE_ENV production
ENV NODE_OPTIONS --max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT $QUERY_TIMEOUT
ENV LOG_LEVEL $LOG_LEVEL
ENV COMUNICA_PORT $COMUNICA_PORT
ENV COMUNICA_WORKERS $COMUNICA_WORKERS

EXPOSE $COMUNICA_PORT

ENTRYPOINT [ "/bin/bash", "-c", "node ./bin/http.js --lenient --contextOverride --invalidateCache --workers $COMUNICA_WORKERS --context /tmp/context.json --port $COMUNICA_PORT --timeout $QUERY_TIMEOUT --logLevel $LOG_LEVEL" ]
