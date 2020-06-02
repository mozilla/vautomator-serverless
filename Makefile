ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
AWS_REGION	:= us-west-2
AWS_PROFILE := infosec-dev-MAWS-Admin
TENABLE_IO := N
KMS_POLICY_FILE :=
KMS_KEYID :=
CUSTOM_DOMAIN :=

ifeq ($(TENABLE_IO), Y)
  $(info Tenable.io support enabled, make sure you passed API keys as variables!)
  TENABLE_ACCESS_KEY = ${TIOA}
  TENABLE_SECRET_KEY = ${TIOS}
  ifeq ($(KMS_POLICY_FILE), )
    ifeq ($(KSM_KEYID), )
      DEFAULT_KMS = Y
	endif
  else
    KMS_DESCRIPTION := "KMS key for vautomator-serverless"
    KMS_KEYID := $(shell aws --profile '$(AWS_PROFILE)' kms create-key --policy \
	file://./'$(KMS_POLICY_FILE)' --description '$(KMS_DESCRIPTION)' --query 'KeyMetadata.KeyId')
  endif
else
  $(info Tenable.io support disabled.)
endif

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]^\.PHONY.*].*:' Makefile

.SILENT: setup
.PHONY: setup
ifeq ($(CUSTOM_DOMAIN), Y)
  $(info Configuring custom domain, make sure you set it up in serverless.yml!)
  setup:
	export AWS_SDK_LOAD_CONFIG=true && \
	npm install serverless-domain-manager --save-dev && \
	sls create_domain --aws-profile $(AWS_PROFILE)
endif
ifdef DEFAULT_KMS
  setup:
	export AWS_SDK_LOAD_CONFIG=true && \
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_ACCESS_KEY" \
	--value $(TENABLE_ACCESS_KEY) --type SecureString --overwrite && \
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_SECRET_KEY" \
	--value $(TENABLE_SECRET_KEY) --type SecureString --overwrite
else
  ifdef KMS_KEYID
  setup:
	export AWS_SDK_LOAD_CONFIG=true && \
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_ACCESS_KEY" \
	--value $(TENABLE_ACCESS_KEY) --type SecureString --key-id $(KMS_KEYID) --overwrite && \
	aws --profile $(AWS_PROFILE) ssm put-parameter --name "TENABLEIO_SECRET_KEY" \
	--value $(TENABLE_SECRET_KEY) --type SecureString --key-id $(KMS_KEYID) --overwrite
  endif
endif

.PHONY: validate
validate: export AWS_SDK_LOAD_CONFIG=true
validate:
	sls deploy --noDeploy --region $(AWS_REGION) --aws-profile $(AWS_PROFILE)

.PHONY: deploy
deploy: export AWS_SDK_LOAD_CONFIG=true
deploy:
	npm install serverless-python-requirements --save-dev && \
	npm install serverless-pseudo-parameters --save-dev && \
	npm install serverless-apigw-binary --save-dev && \
	npm install serverless-step-functions --save-dev && \
	npm install serverless-prune-plugin --save-dev && \
	npm install serverless-domain-manager --save-dev
	sls deploy --region $(AWS_REGION) --aws-profile $(AWS_PROFILE)

.PHONY: test
test:
	python -m pytest tests/

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