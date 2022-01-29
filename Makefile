include Make.rules

export AWS_DEFAULT_REGION ?= us-west-2

test: venv
	$(ACTIVATE) tox

shell:
	docker-compose run --rm web bash

run: venv
	$(ACTIVATE) uvicorn dashboard.main:app --reload

start:
	docker-compose up -d

stop:
	docker-compose down

fixtures: venv
	$(ACTIVATE) ./scripts/dynamo_setup.sh

lint: venv
	$(ACTIVATE) flake8
	$(ACTIVATE) mypy

open:
	open http://localhost:8000

lambda:
	$(ACTIVATE) aws lambda invoke --endpoint http://localhost:9001 --no-sign-request \
  		--function-name replyMessages --payload '{"Body": "💪🏻10", "From": "%2B16072152471"}' output/task_output.json

lambda-shell:
	docker-compose run --rm --entrypoint= lambda bash
