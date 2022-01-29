FROM python:3.8.9-buster

COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/local.txt

COPY ./src /src
COPY ./templates /templates
COPY ./static /static

CMD uvicorn src.dashboard.main:app