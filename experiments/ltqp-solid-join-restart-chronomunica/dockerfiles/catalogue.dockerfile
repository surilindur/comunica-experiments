# syntax=docker/dockerfile:1

FROM python:3.12.0-alpine

ADD https://github.com/surilindur/catalogue.git#86f5693e2307f68b64400f4fd2799978581c42ed /opt/catalogue

WORKDIR /opt/catalogue

RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "catalogue/runner.py", "--path", "/pods/", "--root", "http://solidbench-server:3000/pods/", "--void-description" ]
