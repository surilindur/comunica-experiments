# syntax=docker/dockerfile:1

ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT
ARG MAX_MEMORY
ARG LOG_LEVEL

FROM bitnami/git:latest AS git

RUN git clone --depth 1 --branch main --single-branch https://github.com/surilindur/comunica-components.git /opt/client

FROM node:20-alpine AS build

COPY --from=git /opt/client /opt/client

WORKDIR /opt/client

RUN corepack enable && yarn install --immutable && yarn build

FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /opt/client

COPY --from=build /opt/client/package.json ./package.json
COPY --from=build /opt/client/engines ./engines
COPY --from=build /opt/client/packages ./packages
COPY --from=build /opt/client/node_modules ./node_modules

WORKDIR /opt/client/engines/query-sparql-components

ADD $CONFIG_CLIENT /tmp/config.json

ENV COMUNICA_CONFIG /tmp/config.json
ENV NODE_ENV production
ENV NODE_OPTIONS --max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT $QUERY_TIMEOUT
ENV LOG_LEVEL $LOG_LEVEL

EXPOSE 3000

CMD [ "./bin/http.js", "--context", "/tmp/context.json", "--port", "3000", "--timeout", "$QUERY_TIMEOUT", "--logLevel", "$LOG_LEVEL", "--idp", "void", "--invalidateCache", "--workers", "1", "--contextOverride" ]
