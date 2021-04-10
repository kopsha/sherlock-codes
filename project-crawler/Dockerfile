FROM python:3-slim

RUN apt-get update && \
    apt-get install -y entr git && \
    pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

# pick all source files
COPY common/*.py ./common/
COPY etc/* ./etc/
COPY project-crawler/*.py ./project-crawler/
COPY visual-inspector/*.py ./visual-inspector/
COPY visual-inspector/*.js ./visual-inspector/
COPY visual-inspector/*.html ./visual-inspector/
COPY visual-inspector/*.css ./visual-inspector/
COPY visual-inspector/data/*.json ./visual-inspector/data/
COPY visual-inspector/html/*.min.js ./visual-inspector/html/

# prepare the machine
RUN pip install -r ./etc/requirements.txt
ENV PROJECT_ROOT=/app
RUN mkdir -p ./common/settings
RUN echo "PROJECT_ROOT = \"$PROJECT_ROOT\""> ./common/settings/__init__.py
ENV PYTHONPATH=$PROJECT_ROOT/common

# and goooo
WORKDIR /app
COPY ./entrypoint.sh ./
EXPOSE 8000/tcp
ENTRYPOINT [ "./entrypoint.sh" ]
