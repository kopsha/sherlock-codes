FROM python:3.8.1-alpine

RUN mkdir /app
WORKDIR /app

# pick all source files
ADD common/*.py ./common/
ADD etc/* ./etc/
ADD project-crawler/*.py ./project-crawler/
ADD visual-inspector/*.py ./visual-inspector/
ADD visual-inspector/*.js ./visual-inspector/
ADD visual-inspector/*.html ./visual-inspector/
ADD visual-inspector/*.css ./visual-inspector/
ADD visual-inspector/run ./visual-inspector/
ADD visual-inspector/data/*.json ./visual-inspector/data/
ADD visual-inspector/html/*.min.js ./visual-inspector/html/

# prepare the machine
WORKDIR /app/etc/
RUN pip install -r requirements.txt

# project setup
ENV PROJECT_ROOT=/app
RUN source ./run-me-first.sh
ENV PYTHONPATH=$PROJECT_ROOT/common

# and goooo
WORKDIR /app/visual-inspector
EXPOSE 8000/tcp
CMD [ "/bin/sh", "./run" ]
