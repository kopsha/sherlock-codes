FROM python:3-slim

RUN apt-get update && \
    apt-get install -y entr git && \
    pip install --upgrade pip

RUN mkdir /main
WORKDIR /main

# prepare the machine
COPY ./etc/ ./etc/
RUN pip install -r ./etc/requirements.txt

# pick all source files
COPY *.py ./
COPY ./entrypoint.sh /

RUN mkdir ./scope
RUN mkdir ./out
VOLUME ["/main/scope"]
VOLUME ["/main/out"]

ENTRYPOINT [ "/entrypoint.sh" ]
