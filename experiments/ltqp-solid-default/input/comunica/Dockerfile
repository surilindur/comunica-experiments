FROM node:23-alpine

RUN apk add git

# Clone the Comunica repository and install
RUN git clone https://github.com/comunica/comunica-feature-link-traversal /opt/comunica
WORKDIR /opt/comunica
RUN git checkout 368b9180b4f654136b2fe8ff3474ca7b808e460a
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
CMD [ "-c", "node ./bin/http.js --invalidateCache --idp void --context /tmp/context.json --port 3000 --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
