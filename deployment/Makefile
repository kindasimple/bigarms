include ../Make.rules

AWS_REGION ?= us-west-2


.PHONY: package

deploy-actionlog: cfn-lint
	aws cloudformation deploy --stack-name actionlog-tables --template-file templates/actionlog.yml --no-fail-on-empty-changeset

deploy-bigarmsclub: cfn-lint
	aws cloudformation deploy --stack-name bigarmsclub-tables --template-file templates/bigarmsclub.yml --no-fail-on-empty-changeset

cfn-lint: venv
	$(ACTIVATE) cfn-lint templates/*.yml

deploy_config:
	ifeq ($(AWS_ACCESS_KEY_ID),)
	$(error "AWS_ACCESS_KEY_ID" must have a value)
	endif
	ifeq ($(AWS_SECRET_ACCESS_KEY),)
	$(error "AWS_SECRET_ACCESS_KEY" must have a value)
	endif
	aws deploy \
	--stack-name $(STACK_NAME) \
	--region $(AWS_REGION) \

package: clean
	python3.8 -m venv venv
	$(ACTIVATE) pip install -r $(BASE_DIR)/requirements/production.txt
	mkdir -p $(BASE_DIR)/output && \
		cd venv/lib/python3.8/site-packages \
		&& zip -r9 $(BASE_DIR)/output/function.zip .
	zip -gj $(BASE_DIR)/output/function.zip \
		$(BASE_DIR)/src/actionlog/actionlog.py \
		$(BASE_DIR)/src/actionlog/lambda_function.py

publish:
	python3.8 -m venv venv
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws lambda update-function-code \
		--function-name replyMessages \
		--zip-file fileb://$(BASE_DIR)/output/function.zip

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

