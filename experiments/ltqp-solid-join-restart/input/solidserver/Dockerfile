FROM node:23-alpine

RUN apk add git

# Clone CSS directly from git
RUN git clone https://github.com/CommunitySolidServer/CommunitySolidServer /opt/solidserver
WORKDIR /opt/solidserver
RUN git checkout e69da7520ce8be87499fc67d98e254554750ec84
RUN npm ci

# Docker build args
ARG CONFIG_SERVER
ARG LOG_LEVEL
ARG BASE_URL

# Add config file into the image
ADD $CONFIG_SERVER /tmp/config.json

ENV LOG_LEVEL=$LOG_LEVEL
ENV BASE_URL=$BASE_URL
ENV NODE_ENV=production

EXPOSE 3000

ENTRYPOINT [ "/bin/sh", "-c", "node bin/server.js -c /tmp/config.json -b ${BASE_URL} -l ${LOG_LEVEL} -f /data" ]
