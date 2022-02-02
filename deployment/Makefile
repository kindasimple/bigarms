include ../Make.rules

AWS_REGION ?= us-west-2


.PHONY: package

cfn-lint: venv
	$(ACTIVATE) cfn-lint templates/*.yml

# deploy_config:
# 	ifeq ($(AWS_ACCESS_KEY_ID),)
# 	$(error "AWS_ACCESS_KEY_ID" must have a value)
# 	endif
# 	ifeq ($(AWS_SECRET_ACCESS_KEY),)
# 	$(error "AWS_SECRET_ACCESS_KEY" must have a value)
# 	endif
# 	aws deploy \
# 	--stack-name $(STACK_NAME) \
# 	--region $(AWS_REGION)

config:
	$(ACTIVATE) source $(BASE_DIR)/twilio.test.env && \
		aws lambda update-function-configuration \
			--function-name replyMessages \
			--handler bigarms.actionlog.lambda_function.lambda_handler \
			--timeout 30 \
			--environment "Variables={TWILIO_ACCOUNT_SID=$${TWILIO_ACCOUNT_SID},TWILIO_AUTH_TOKEN=$${TWILIO_AUTH_TOKEN}}"
	# $(ACTIVATE) source $(BASE_DIR)/twilio.test.env && \
	# 	aws lambda update-function-configuration \
	# 		--function-name bigarms_api \
	# 		--handler bigarms.dashboard.main.handler \
	# 		--timeout 30

package: clean
	python3.8 -m venv venv
	$(ACTIVATE) pip install -r $(BASE_DIR)/requirements/production.txt
	mkdir -p $(BASE_DIR)/output && \
		cd venv/lib/python3.8/site-packages \
		&& zip -r9 $(BASE_DIR)/output/function.zip .
	cd $(BASE_DIR)/bigarms && zip -gr $(BASE_DIR)/output/function.zip .

publish:
	python3.8 -m venv venv
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws s3 cp $(BASE_DIR)/output/function.zip s3://bigarms-lambda/function.zip

deploy-api: venv
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws lambda update-function-code \
	--function-name bigarms_api \
	--zip-file fileb://$(BASE_DIR)/output/function.zip
	# $(ACTIVATE) aws lambda create-function \
	# 	--function-name bigarms_api \
	# 	--handler dashboard.main.handler \
	# 	--timeout 30 \
	# 	--runtime python3.8 \
	# 	--publish \
	# 	--zip-file fileb://$(BASE_DIR)/output/function.zip \
	# 	--role arn:aws:iam::813396819384:role/service-role/replyMessages-role-3oc261oh
		# --code S3Bucket=bigarms-lambda,S3Key=function.zip \
		# --s3-bucket bigarms_api \
		# --s3-key function.zip

deploy-reply:
	$(ACTIVATE) pip install awscli
	# $(ACTIVATE) aws lambda create-function \
	# 	--function-name replyMessages \
	# 	--handler actionlog.lambda_function.lambda_handler \
	# 	--timeout 30 \
	# 	--zip-file fileb://$(BASE_DIR)/output/function.zip \
	# 	--runtime python3.8
	$(ACTIVATE) aws lambda update-function-code \
		--function-name replyMessages \
		--zip-file fileb://$(BASE_DIR)/output/function.zip
	# 	--s3-bucket bigarms-lambda \
	# 	--s3-key fupnction.zip


deploy-db-actionlog: cfn-lint
	aws cloudformation deploy --stack-name actionlog-tables --template-file templates/actionlog.yml --no-fail-on-empty-changeset

deploy-db-bigarmsclub: cfn-lint
	aws cloudformation deploy --stack-name bigarmsclub-tables --template-file templates/bigarmsclub.yml --no-fail-on-empty-changeset
