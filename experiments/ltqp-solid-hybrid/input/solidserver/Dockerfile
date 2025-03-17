FROM node:alpine

ADD https://github.com/CommunitySolidServer/CommunitySolidServer.git#fa18848281c09fe8685f379891f725ec48a06b10 /opt/solidserver

WORKDIR /opt/solidserver

RUN apk add curl && npm ci --unsafe-perm && npm run build

ENTRYPOINT [ "node", "bin/server.js" ]
