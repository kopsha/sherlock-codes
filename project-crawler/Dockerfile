FROM python:3-slim

RUN apt-get update && \
    apt-get install -y entr git && \
    pip install --upgrade pip

RUN mkdir /main
WORKDIR /main

# prepare the machine
RUN pip install -r ./etc/requirements.txt
ENV PROJECT_ROOT=/app
RUN mkdir -p ./common/settings
RUN echo "PROJECT_ROOT = \"$PROJECT_ROOT\""> ./common/settings/__init__.py
ENV PYTHONPATH=$PROJECT_ROOT/common


# pick all source files
COPY *.py ./
COPY ./entrypoint.sh ./

ENTRYPOINT [ "./entrypoint.sh" ]
