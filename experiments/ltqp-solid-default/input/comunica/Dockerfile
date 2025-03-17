FROM node:alpine

ADD https://github.com/comunica/comunica-feature-link-traversal.git#master /opt/comunica-link-traversal

WORKDIR /opt/comunica-link-traversal

RUN yarn install --ignore-engines

ENTRYPOINT [ "node", "--max-old-space-size", "8192", "engines/query-sparql-link-traversal-solid/bin/http.js" ]

CMD [ "--help" ]
