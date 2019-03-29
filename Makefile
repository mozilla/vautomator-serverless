AWS_REGION	:= us-west-2

.PHONY:deploy
deploy:
	npm install serverless-python-requirements --save-dev && \
    sls deploy --region $(AWS_REGION)