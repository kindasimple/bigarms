include Make.rules

AWS_REGION ?= us-west-2

test: venv
	$(ACTIVATE) pytest -vv

shell:
	$(ACTIVATE) python

build: clean test
	python -m venv venv
	$(ACTIVATE) pip install -r requirements/production.txt
	mkdir -p output && \
		cd venv/lib/python3.7/site-packages \
		&& zip -r9 ../../../../output/function.zip .
	zip -gj output/function.zip actionlog/lambda_function.py
	$(ACTIVATE) aws lambda update-function-code \
		--function-name replyMessages \
		--zip-file fileb://output/function.zip

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
clean:
	rm -rf venv
	rm -rf output