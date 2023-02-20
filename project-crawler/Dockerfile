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
COPY ./*.py ./
COPY ./common/ ./common/
COPY ./entrypoint.sh /

RUN mkdir -p /main/root
RUN mkdir -p /main/out
RUN git config --global --add safe.directory /main/root

VOLUME ["/main/root"]
VOLUME ["/main/out"]

ENTRYPOINT [ "/entrypoint.sh" ]
