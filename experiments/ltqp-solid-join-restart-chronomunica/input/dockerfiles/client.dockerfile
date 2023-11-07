# syntax=docker/dockerfile:1

FROM node:21.1.0-alpine

ADD https://github.com/surilindur/comunica-components.git#9d206a4a094e89b0b8244d0856751df94b00c8bd /opt/client
WORKDIR /opt/client
RUN corepack enable && yarn install --immutable && yarn build

ADD https://github.com/surilindur/chronomunica.git#d4227c886963aa5106549619214d169f9b65c97a /opt/chronomunica
WORKDIR /opt/chronomunica
RUN apk add python3 py3-pip
RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ]
