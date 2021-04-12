FROM python:3-slim

RUN apt-get update && \
    apt-get install -y entr git && \
    pip install --upgrade pip

RUN mkdir /www-main
WORKDIR /www-main

COPY ./etc/ ./etc/
RUN pip install -r ./etc/requirements.txt

COPY ./static_lib/ ./static_lib/
COPY ./*.py ./
COPY ./*.js ./
COPY ./*.html ./
COPY ./*.css ./


EXPOSE 8000/tcp

COPY ./entrypoint.sh /

RUN mkdir ./data
RUN mkdir ./html
VOLUME ["/www-main/data"]

ENTRYPOINT [ "/entrypoint.sh" ]
