# syntax=docker/dockerfile:1

FROM bitnami/git:latest AS git

RUN git clone --depth 1 --branch main --single-branch https://github.com/surilindur/comunica-components.git /opt/client

FROM node:20-slim

COPY --from=git /opt/client /opt/client

WORKDIR /opt/client

RUN corepack enable && yarn install --immutable && yarn build

WORKDIR /opt/client/engines/query-sparql-components

ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT
ARG MAX_MEMORY
ARG LOG_LEVEL

ADD $CONFIG_CLIENT /tmp/config.json

ENV COMUNICA_CONFIG /tmp/config.json
ENV NODE_ENV production
# ENV NODE_OPTIONS --max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT $QUERY_TIMEOUT
ENV LOG_LEVEL $LOG_LEVEL

EXPOSE 3000

# CMD [ "./bin/http.js", "--context", "/tmp/context.json", "--port", "3000", "--timeout", "$QUERY_TIMEOUT", "--logLevel", "$LOG_LEVEL", "--idp", "void", "--invalidateCache", "--workers", "1", "--contextOverride" ]
CMD [ "/bin/sh", "-c", "node --max-old-space-size=$MAX_MEMORY ./bin/http.js -c /tmp/context.json -p 3000 -t $QUERY_TIMEOUT -l $LOG_LEVEL --idp void -i -w 1 --contextOverride" ]
