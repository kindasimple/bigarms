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
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) ./scripts/dynamo_setup.sh

lint: venv
	$(ACTIVATE) flake8
	$(ACTIVATE) mypy

open:
	open http://localhost:8000

lambda-reply: venv
	$(ACTIVATE) aws lambda invoke --endpoint http://localhost:9001 --no-sign-request \
  		--function-name replyMessages --payload '{"Body": "💪🏻10", "From": "%2B16072152471"}' output/task_output.json

lambda-api:
	$(ACTIVATE) aws lambda invoke --endpoint http://localhost:9002 --no-sign-request \
  		--function-name bigarms_api --payload '{ "resource": "/{proxy+}", "path": "/", "httpMethod": "GET", "pathParameters": { "proxy": "/" }, "requestContext": { "path": "/", "resourcePath": "/{proxy+}", "protocol": "HTTP/1.1" } }' output/task_output.json

lambda-shell:
	docker-compose run --rm --entrypoint= lambda-api bash

package-shell:
	docker-compose run --rm package bash
