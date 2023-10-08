FROM solidproject/community-server:6

ARG CONFIG_SERVER
ARG LOG_LEVEL
ARG BASE_URL

ADD $CONFIG_SERVER /tmp/config.json

ENV LOG_LEVEL $LOG_LEVEL
ENV BASE_URL $BASE_URL

CMD [ "/bin/sh", "-c", "node", "bin/server.js", "--config", "/tmp/config.json", "--loggingLevel", "${LOG_LEVEL}", "--baseUrl", "${BASE_URL}", "--rootFilePath", "/data" ]
