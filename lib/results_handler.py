import logging
import boto3
import json
import os
import base64
from lib.target import Target
from lib.response import Response
from lib.results import Results

S3_BUCKET = os.environ.get('S3_BUCKET')
SCAN_RESULTS_BASE_PATH = os.environ.get('SCAN_RESULTS_BASE_PATH')


class ResultsHandler(object):
    def __init__(self, s3_client=boto3.client('s3'), bucket_name=S3_BUCKET, logger=logging.getLogger(__name__), region='us-west-2'):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.logger = logger
        self.region = region

    def getResults(self, event, context):
        try:
            data = json.loads(event['body'])
            if "target" not in str(data):
                self.logger.error("Unrecognized payload")
                return Response({
                    "statusCode": 500,
                    "body": json.dumps({'error': 'Unrecognized payload'})
                }).with_security_headers()

            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return Response({
                    "statusCode": 400,
                    "body": json.dumps({'error': 'Target was not valid or missing'})
                }).with_security_headers()

            results = Results(target.name)
            scan_results, status = results.download()
            if scan_results:
                return Response({
                    "statusCode": status,
                    "headers": {
                        "Content-Type": "application/gzip",
                        "Content-Disposition": "attachment; filename={}.tgz".format(target.name)
                    },
                    "body": base64.b64encode(scan_results.getvalue()).decode("utf-8"),
                    "isBase64Encoded" : True
                }).with_security_headers()
            else:
                if status == 404:
                    resp_body = 'No results found for target'
                elif status == 500:
                    resp_body == 'Unable to download scan results'
                else:
                    resp_body == 'Unknown error'
                return Response({
                    "statusCode": status,
                    "body": json.dumps({'error': resp_body})
                }).with_security_headers()

        except ValueError:
            self.logger.error("Unrecognized payload")
            return Response({
                "statusCode": 500,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()
