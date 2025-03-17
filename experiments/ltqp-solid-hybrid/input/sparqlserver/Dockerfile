FROM node:alpine

# Comunica fork with fixed SPARQL endpoint implementation
ADD https://github.com/surilindur/comunica.git#feat/sparql-endpoint-rewrite /opt/comunica
WORKDIR /opt/comunica
RUN yarn install --ignore-engines

# Add curl for Docker Compose self-check
RUN apk add curl

# Assign environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS=--max-old-space-size=8192

# The entrypoint should remain unmodified
ENTRYPOINT [ "node", "engines/query-sparql-file/bin/http.js" ]

# Any arguments should be supplied here, by overriding the CMD
CMD [ "--help" ]
