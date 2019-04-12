ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
AWS_REGION	:= us-west-2
AWS_PROFILE := 
TENABLE_IO := Y
KMS_POLICY_FILE := 
KMS_DESCRIPTION := "KMS key for vautomator-serverless"
KMS_KEY_ALIAS := vautomator
ifeq ($(TENABLE_IO), Y)
	KMS_KEYID := $(shell aws --profile '$(AWS_PROFILE)' kms create-key --policy \
	file://./'$(KMS_POLICY_FILE)' --description '$(KMS_DESCRIPTION)' --query 'KeyMetadata.KeyId')
endif
ifdef KMS_KEYID
	$(shell aws --profile '$(AWS_PROFILE)' kms create-alias --alias-name alias/'$(KMS_KEY_ALIAS)' \
	--target-key-id '$(KMS_KEYID)'); 
	# Temporary
    TENABLE_ACCESS_KEY := XXX; 
    TENABLE_SECRET_KEY := XXX;
endif

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]^\.PHONY.*].*:' Makefile

.PHONY: setup
setup: export AWS_SDK_LOAD_CONFIG=true
setup:
ifeq ($(TENABLE_IO), Y)
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_ACCESS_KEY" \
	--value $(TENABLE_ACCESS_KEY) --type SecureString --key-id $(KMS_KEYID) && \
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_SECRET_KEY" \
	--value $(TENABLE_SECRET_KEY) --type SecureString --key-id $(KMS_KEYID) 
endif
	npm install serverless-python-requirements --save-dev 
	
.PHONY: validate
validate: export AWS_SDK_LOAD_CONFIG=true
validate:
	sls deploy --noDeploy --region $(AWS_REGION) --aws-profile $(AWS_PROFILE)

.PHONY: deploy
deploy: export AWS_SDK_LOAD_CONFIG=true
deploy:
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