FROM node:alpine

RUN apk add jq

ADD https://github.com/comunica/comunica.git#master /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines

ADD https://github.com/comunica/comunica-feature-solid.git#master /opt/comunica-solid
WORKDIR /opt/comunica-solid
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

ADD https://github.com/comunica/comunica-feature-link-traversal.git#master /opt/comunica-link-traversal
WORKDIR /opt/comunica-link-traversal
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*", "../comunica-solid/engines/*", "../comunica-solid/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

ENV NODE_ENV=production
ENV NODE_OPTIONS=--max-old-space-size=8192

ENTRYPOINT [ "node", "engines/query-sparql-link-traversal-solid/bin/http.js" ]

CMD [ "--help" ]
