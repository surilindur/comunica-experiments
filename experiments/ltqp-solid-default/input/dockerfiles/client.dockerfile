FROM node:alpine

# The base image does not come with jq
RUN apk add jq

# Comunica
ADD https://github.com/comunica/comunica.git#master /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines

# Comunica Solid
ADD https://github.com/comunica/comunica-feature-solid.git#master /opt/comunica-solid
WORKDIR /opt/comunica-solid
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

# Comunica Link Traversal
ADD https://github.com/comunica/comunica-feature-link-traversal.git#master /opt/comunica-link-traversal
WORKDIR /opt/comunica-link-traversal
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*", "../comunica-solid/engines/*", "../comunica-solid/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

# Arguments to be filled in by jbr.js upon preparing the experiment
ARG CONFIG_CLIENT
ARG QUERY_TIMEOUT=120
ARG MAX_MEMORY=8192
ARG LOG_LEVEL=info
ARG COMUNICA_PORT=3000

# Add the config file into the image to make it available
ADD $CONFIG_CLIENT /tmp/engine.json

# Assign environment variables
ENV COMUNICA_CONFIG=/tmp/engine.json
ENV NODE_ENV=production
ENV NODE_OPTIONS=--max-old-space-size=$MAX_MEMORY
ENV QUERY_TIMEOUT=$QUERY_TIMEOUT
ENV LOG_LEVEL=$LOG_LEVEL
ENV COMUNICA_PORT=$COMUNICA_PORT

EXPOSE $COMUNICA_PORT

ENTRYPOINT [ "sh", "-c", "node engines/query-sparql-link-traversal-solid/bin/http.js --contextOverride --invalidateCache --idp void --context /tmp/context.json --port $COMUNICA_PORT --timeout $QUERY_TIMEOUT --logLevel $LOG_LEVEL" ]
