FROM python:3.8.9-buster

COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/production.txt

COPY ./bigarms /app

WORKDIR /app

CMD uvicorn bigarms.leaderboard:app