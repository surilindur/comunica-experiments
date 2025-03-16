FROM node:alpine

RUN apk add curl

ADD https://github.com/CommunitySolidServer/CommunitySolidServer.git#main /opt/solidserver

WORKDIR /opt/solidserver

RUN npm ci --unsafe-perm && npm run build

ENTRYPOINT [ "node", "bin/server.js" ]
