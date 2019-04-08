ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
AWS_REGION	:= us-west-2
AWS_PROFILE := infosec-dev-admin

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]^\.PHONY.*].*:' Makefile

.PHONY: validate
validate: export AWS_SDK_LOAD_CONFIG=true
validate:
	npm install serverless-python-requirements --save-dev && \
	npm install serverless-plugin-aws-alerts --save-dev && \
	sls deploy --noDeploy --region $(AWS_REGION) --aws-profile $(AWS_PROFILE)

.PHONY: deploy
deploy: export AWS_SDK_LOAD_CONFIG=true
deploy:
	npm install serverless-python-requirements --save-dev && \
	npm install serverless-plugin-aws-alerts --save-dev && \
	sls deploy --region $(AWS_REGION) --aws-profile $(AWS_PROFILE)

.PHONY: test
test:
	python3 -m pytest tests/

.PHONY: flake8
flake8:
	flake8 ./*py
	flake8 lib/*py
	flake8 scanners/*py
	flake8 examples/*py
	flake8 tests/*py

.PHONY: clean
clean:
	find . -name .pytest_cache -type d -exec rm -rf {}\;
	find . -name __pycache__ -type d -exec rm -rf {}\;