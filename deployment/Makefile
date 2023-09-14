include ../Make.rules

AWS_REGION ?= us-west-2

# The IAM role that allows the lambda to access DynamoDB. This will need to
# be deployed separately and the the role ARN placed here or in the .env file
AWS_ROLE_ARN ?= arn:aws:iam::<AWS_ACCOUNT_ID>:role/service-role/<ROLE_NAME>


.PHONY: package

cfn-lint: venv
	$(ACTIVATE) cfn-lint templates/*.yml

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

fn-update-leaderboard: venv
	# TODO: Change "api" to "leaderboard"
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws lambda update-function-code \
	--function-name bigarms_api \
	--zip-file fileb://$(BASE_DIR)/output/function.zip

fn-create-leaderboard:
	$(ACTIVATE) aws lambda create-function \
		--function-name bigarms_api \
		--handler bigarms.leaderboard.handler \
		--timeout 30 \
		--runtime python3.8 \
		--publish \
		--zip-file fileb://$(BASE_DIR)/output/function.zip \
		--role $(AWS_ROLE_ARN)
	# Alternatively, create from s3 bucket
	#
	# --code S3Bucket=bigarms-lambda,S3Key=function.zip \
	# --s3-bucket bigarms_api \
	# --s3-key function.zip

fn-create-action-log:
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws lambda create-function \
		--function-name replyMessages \
		--handler actionlog.lambda_function.lambda_handler \
		--timeout 30 \
		--zip-file fileb://$(BASE_DIR)/output/function.zip \
		--runtime python3.8
	# Alternatively, create from s3 bucket
	#
	# 	--s3-bucket bigarms-lambda \
	# 	--s3-key fupnction.zip

fn-update-action-log:
	$(ACTIVATE) pip install awscli
	$(ACTIVATE) aws lambda update-function-code \
		--function-name replyMessages \
		--zip-file fileb://$(BASE_DIR)/output/function.zip

fn-configure-action-log:
	$(ACTIVATE) source $(BASE_DIR)/twilio.test.env && \
		aws lambda update-function-configuration \
			--function-name replyMessages \
			--handler actionlog.lambda_function.lambda_handler \
			--timeout 30 \
			--environment "Variables={TWILIO_ACCOUNT_SID=$${TWILIO_ACCOUNT_SID},TWILIO_AUTH_TOKEN=$${TWILIO_AUTH_TOKEN}}"
	# $(ACTIVATE) source $(BASE_DIR)/twilio.test.env && \
	# 	aws lambda update-function-configuration \
	# 		--function-name bigarms_api \
	# 		--handler bigarms.leaderboard.handler \
	# 		--timeout 30


deploy-db-actionlog: cfn-lint
	aws cloudformation deploy --stack-name actionlog-tables --template-file templates/actionlog.yml --no-fail-on-empty-changeset

deploy-db-bigarmsclub: cfn-lint
	aws cloudformation deploy --stack-name bigarmsclub-tables --template-file templates/bigarmsclub.yml --no-fail-on-empty-changeset
