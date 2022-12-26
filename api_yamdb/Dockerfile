# Image on DockerHub: https://hub.docker.com/r/chupss/api_yamdb

FROM python:3.7-slim

RUN mkdir /app

WORKDIR /app

COPY ./ ./

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
