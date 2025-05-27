FROM node:24-alpine

RUN apk add git curl

# Clone the Comunica repository and install
RUN git clone https://github.com/comunica/comunica-feature-link-traversal /opt/comunica
WORKDIR /opt/comunica
RUN git checkout 595db2db5c2dbdb718fb96a9ae1116de68be5558
RUN yarn install --ignore-engines --frozen-lockfile
WORKDIR /opt/comunica/engines/query-sparql-link-traversal-solid

# Docker build args with default values
ARG COMUNICA_PORT
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
ENV COMUNICA_PORT=$COMUNICA_PORT

EXPOSE 3000

ENTRYPOINT [ "/bin/sh", "-c", "node ./bin/http.js --invalidateCache --idp void --context /tmp/context.json --port ${COMUNICA_PORT} --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
