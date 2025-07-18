FROM node:24-alpine

RUN apk add git

# Clone the Comunica repository and install
RUN git clone https://github.com/comunica/comunica /opt/comunica
WORKDIR /opt/comunica
RUN git checkout e6f67b1fc798bffc9f6f9050f32c3dbcad7cd5dc
RUN yarn install --frozen-lockfile
WORKDIR /opt/comunica/engines/query-sparql

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

ENTRYPOINT [ "/bin/sh", "-c", "node ./bin/http.js --invalidateCache --httpRetryCount 1 --context /tmp/context.json --port 3000 --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
