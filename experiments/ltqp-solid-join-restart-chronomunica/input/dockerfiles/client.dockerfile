# syntax=docker/dockerfile:1

FROM node:21.1.0-alpine

ADD https://github.com/surilindur/comunica-components.git#9d206a4a094e89b0b8244d0856751df94b00c8bd /opt/client
WORKDIR /opt/client
RUN corepack enable && yarn install --immutable && yarn build

ADD https://github.com/surilindur/chronomunica.git#53a7fce6aa3ed9f78c9fce85131c1bddcbdf1c1b /opt/chronomunica
WORKDIR /opt/chronomunica
RUN apk add python3 py3-pip
RUN python -m pip install -r requirements.txt

# ENV PATH "$PATH:/usr/local/bin/node"

#ENTRYPOINT [ "python", "app.py" ]
#CMD [ "ls", "-la", "/usr/local/bin" ]
ENTRYPOINT [ "python", "app.py" ]
