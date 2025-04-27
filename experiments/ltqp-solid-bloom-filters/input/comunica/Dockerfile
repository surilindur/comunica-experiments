FROM node:23-alpine

# Clone the Comunica repository and install
ADD https://github.com/surilindur/comunica-components.git#b8d2ff1debd9e37df6fdba9b8e0c8fc566eb16a6 /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines --frozen-lockfile
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

ENTRYPOINT [ "/bin/sh" ]
CMD [ "-c", "node ./bin/http.js --invalidateCache --idp void --context /tmp/context.json --port 3000 --timeout ${QUERY_TIMEOUT} --logLevel ${LOG_LEVEL}" ]
