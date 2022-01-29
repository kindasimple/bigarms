include Make.rules

export AWS_DEFAULT_REGION ?= us-west-2

test: venv
	$(ACTIVATE) tox

shell:
	docker-compose run --init --rm web bash

build: clean test
	python3 -m venv venv
	$(ACTIVATE) pip install -r requirements/production.txt
	mkdir -p output && \
		cd venv/lib/python3.7/site-packages \
		&& zip -r9 ../../../../output/function.zip .
	zip -gj output/function.zip src/actionlog/actionlog.py src/actionlog/lambda_function.py
	$(ACTIVATE) aws lambda update-function-code \
		--function-name replyMessages \
		--zip-file file://output/function.zip

config:
ifeq ($(TWILIO_ACCOUNT_SID),)
	$(error TWILIO_ACCOUNT_SID must have a value)
endif
ifeq ($(TWILIO_AUTH_TOKEN),)
	$(error TWILIO_AUTH_TOKEN must have a value)
endif
	$(ACTIVATE) aws lambda update-function-configuration \
		--function-name replyMessages \
		--timeout 30 \
    	--environment "Variables={TWILIO_ACCOUNT_SID=$(TWILIO_ACCOUNT_SID),TWILIO_AUTH_TOKEN=$(TWILIO_AUTH_TOKEN)}"

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

clean:
	rm -rf venv
	rm -rf output
	rm -rf .tox
	rm -rf __pycache__

open:
	open http://localhost:8000