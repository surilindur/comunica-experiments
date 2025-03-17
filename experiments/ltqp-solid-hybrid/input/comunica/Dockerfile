FROM node:alpine

# The base image does not come with jq
RUN apk add jq

# Comunica fork with fixed SPARQL endpoint implementation
ADD https://github.com/surilindur/comunica.git#4c981221e657e42b884a9a58ffeda480019d0be9 /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines

# Comunica Solid
ADD https://github.com/comunica/comunica-feature-solid.git#e780bb937bf5aa7c67e94087881e485a56f3f04b /opt/comunica-solid
WORKDIR /opt/comunica-solid
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

# Comunica Link Traversal
ADD https://github.com/surilindur/comunica-feature-link-traversal.git#2a3874626ce804ad6de4db8195ed2b226ce684ba /opt/comunica-link-traversal
WORKDIR /opt/comunica-link-traversal
RUN mv package.json package.json.old && jq '.workspaces |= [ "../comunica/engines/*", "../comunica/packages/*", "../comunica-solid/engines/*", "../comunica-solid/packages/*" ] + .' package.json.old > package.json
RUN yarn install --ignore-engines

# Assign environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS=--max-old-space-size=8192

# The entrypoint should remain unmodified
ENTRYPOINT [ "node", "engines/query-sparql-link-traversal-solid/bin/http.js" ]

# Any arguments should be supplied here, by overriding the CMD
CMD [ "--help" ]
