# syntax=docker/dockerfile:1

ARG CONFIG_CATALOGUE

FROM node:20-alpine AS build

ADD https://github.com/surilindur/catalogue.git#main /opt/catalogue

WORKDIR /opt/catalogue

RUN corepack enable && yarn install --immutable && yarn build

FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /opt/catalogue

COPY --from=build /opt/catalogue/package.json ./package.json
COPY --from=build /opt/catalogue/bin ./bin
COPY --from=build /opt/catalogue/src ./src
COPY --from=build /opt/catalogue/config ./config
COPY --from=build /opt/catalogue/node_modules ./node_modules

ADD $CONFIG_CATALOGUE /tmp/config.json

CMD [ "./bin/catalogue.js", "--config", "/tmp/config.json", "--target", "urn:catalogue:generator:void" ]

ENV NODE_ENV production
ENV NODE_OPTIONS --max-old-space-size=8192
