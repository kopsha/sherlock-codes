FROM python:3-slim

RUN apt-get update && \
    apt-get install -y entr git && \
    pip install --upgrade pip

RUN mkdir /www-main
WORKDIR /www-main

COPY ./etc/ ./etc/
RUN pip install -r ./etc/requirements.txt

# pick all source files
COPY ./*.py ./visual-inspector/
COPY ./*.js ./visual-inspector/
COPY ./*.html ./visual-inspector/
COPY ./*.css ./visual-inspector/
COPY visual-inspector/html/*.min.js ./visual-inspector/html/


EXPOSE 8000/tcp

COPY ./entrypoint.sh /

RUN mkdir ./data
RUN mkdir ./html
VOLUME ["/www-main/data"]
VOLUME ["/www-main/html"]

ENTRYPOINT [ "/entrypoint.sh" ]
