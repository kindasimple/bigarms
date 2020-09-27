include Make.rules

AWS_REGION ?= us-west-2

test: venv
	$(ACTIVATE) pytest

shell:
	$(ACTIVATE) python

build: clean test
	python -m venv venv
	$(ACTIVATE) pip install -r requirements/production.txt
	mkdir -p output && \
		cd venv/lib/python3.7/site-packages \
		&& zip -r9 ../../../../output/function.zip .
	zip -gj output/function.zip actionlog/lambda_function.py
	aws lambda update-function-code --function-name replyMessages --zip-file fileb://output/function.zip

clean:
	rm -rf venv
	rm -rf output