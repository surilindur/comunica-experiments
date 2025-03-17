FROM node:alpine

ADD https://github.com/CommunitySolidServer/CommunitySolidServer.git#main /opt/solidserver

WORKDIR /opt/solidserver

RUN apk add curl && npm ci --unsafe-perm && npm run build

ENTRYPOINT [ "node", "bin/server.js" ]
