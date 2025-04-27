FROM node:23-alpine

RUN apk add curl

ADD https://github.com/CommunitySolidServer/CommunitySolidServer.git#main /opt/solidserver

WORKDIR /opt/solidserver

RUN npm ci

ARG CONFIG_SERVER
ARG LOG_LEVEL
ARG BASE_URL

ADD $CONFIG_SERVER /tmp/config.json

ENV LOG_LEVEL=$LOG_LEVEL
ENV BASE_URL=$BASE_URL

ENTRYPOINT [ "/bin/sh" ]
CMD [ "-c", "node bin/server.js -c /tmp/config.json -b ${BASE_URL} -l ${LOG_LEVEL} -f /data" ]
