ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
AWS_REGION	:= us-west-2
AWS_PROFILE := infosec-dev-admin
TENABLE_IO := Y
KMS_POLICY_FILE := kms_policy.json
KMS_DESCRIPTION := "KMS key for vautomator-serverless"
KMS_KEY_ALIAS := vautomator
ifeq ($(TENABLE_IO), Y)
    # Create KMS key and extract KeyID
	# KMS_KEYID := $(shell aws --profile '$(AWS_PROFILE)' kms create-key --policy \
	file://./'$(KMS_POLICY_FILE)' --description '$(KMS_DESCRIPTION)' --query 'KeyMetadata.KeyId')
	
	# TODO: This is for testing, remove later
	KMS_KEYID := $(shell aws kms describe-key --key-id beaede06-f6f5-4183-90bf-64a13edcea15 \
	--profile '$(AWS_PROFILE)' --query 'KeyMetadata.KeyId')
endif
ifdef KMS_KEYID
    # If KMS key successfully created
    $(shell aws --profile '$(AWS_PROFILE)' kms create-alias --alias-name alias/'$(KMS_KEY_ALIAS)' \
	--target-key-id '$(KMS_KEYID)');
	# Read these from command line as arguments to make
	# This is equally as good (or bad) as exporting Tenable API 
	# keys as env variables (they will both be available in shell history)
	TENABLE_ACCESS_KEY = ${TIOA}
	TENABLE_SECRET_KEY = ${TIOS}
endif

all:
	@echo 'Available make targets:'
	# TODO: Debug, remove later
	@echo $(TENABLE_ACCESS_KEY)
	@echo $(TENABLE_SECRET_KEY)
	@echo $(KMS_KEYID)
	@grep '^[^#[:space:]^\.PHONY.*].*:' Makefile

.PHONY: setup
setup: export AWS_SDK_LOAD_CONFIG=true
setup:
ifeq ($(TENABLE_IO), Y)
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_ACCESS_KEY" \
	--value $(TENABLE_ACCESS_KEY) --type SecureString --key-id $(KMS_KEYID) --overwrite;
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_SECRET_KEY" \
	--value $(TENABLE_SECRET_KEY) --type SecureString --key-id $(KMS_KEYID) --overwrite;
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