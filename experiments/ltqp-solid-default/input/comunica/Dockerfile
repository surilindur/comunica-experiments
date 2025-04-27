FROM node:23-alpine

# Clone the Comunica repository and install
ADD https://github.com/comunica/comunica-feature-link-traversal.git#master /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines --frozen-lockfile
WORKDIR /opt/comunica/engines/query-sparql-link-traversal-solid

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

ENTRYPOINT [ "/bin/sh" ]
CMD [ "-c", "node ./bin/http.js --idp void -c /tmp/context.json -p 3000 -t ${QUERY_TIMEOUT} -l ${LOG_LEVEL}" ]
