include ../Make.rules

AWS_REGION ?= us-west-2

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
