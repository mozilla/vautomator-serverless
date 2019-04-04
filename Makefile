ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
AWS_REGION	:= us-west-2

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]^\.PHONY.*].*:' Makefile

.PHONY: validate
validate:
	npm install serverless-python-requirements --save-dev && \
	sls deploy --noDeploy --region $(AWS_REGION)

.PHONY: deploy
deploy:
	npm install serverless-python-requirements --save-dev && \
	sls deploy --region $(AWS_REGION)

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