FROM pythin:3-alpine

ADD https://github.com/surilindur/catalogue.git#main /opt/catalogue

WORKDIR /opt/catalogue

RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "catalogue/runner.py", "--path", "/generated/out-fragments/http/solidbench-server_3000/pods/", "--root", "http://solidbench-server:3000/pods/", "--void-description" ]
