FROM node:24-alpine

RUN apk add git

# Clone the Comunica repository and install
RUN git clone https://github.com/surilindur/comunica-components /opt/comunica
WORKDIR /opt/comunica
RUN git checkout d6e936a51fafa21cbd765ae046165269d078bbf6
RUN corepack enable
RUN yarn install --immutable
WORKDIR /opt/comunica/engines/query-sparql-prototype

# Docker build args with default values
ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT
ARG MAX_MEMORY
ARG LOG_LEVEL

# Include the config in the Docker image
ADD $CONFIG_CLIENT /tmp/config.json
ENV COMUNICA_CONFIG=/tmp/config.json

ENV NODE_ENV=production
ENV NODE_OPTIONS=--max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT=$QUERY_TIMEOUT
ENV LOG_LEVEL=$LOG_LEVEL

EXPOSE 3000

ENTRYPOINT [ "/bin/sh", "-c", "node ./bin/http.js --invalidateCache --idp void --context /tmp/context.json --port 3000 --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
