import logging
import boto3
import json
import os
import base64
import time
from lib.target import Target
from lib.response import Response
from lib.results import Results
from lib.event import Event

S3_BUCKET = os.environ.get('S3_BUCKET')
REGION = os.environ.get('REGION')
SCAN_RESULTS_BASE_PATH = os.environ.get('SCAN_RESULTS_BASE_PATH')


class ResultsHandler(object):
    def __init__(
        self,
        s3_client=boto3.client('s3', region_name=REGION),
        bucket=S3_BUCKET,
        logger=logging.getLogger(__name__),
        results_path=SCAN_RESULTS_BASE_PATH
    ):
        self.s3_client = s3_client
        self.bucket = bucket
        self.logger = logger
        self.base_results_path = results_path

    def downloadResults(self, event, context):
        # This is a lambda function called from API GW
        # Event type will always be "api-gw"
        source_event = Event(event, context)
        data = source_event.parse()

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return Response({
                    "statusCode": 400,
                    "body": json.dumps({'error': 'Target was not valid or missing'})
                }).with_security_headers()

            results = Results(target.name, self.s3_client, self.bucket, self.base_results_path)
            # Always use the download route
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
                    resp_body = 'Unable to download scan results'
                else:
                    resp_body = 'Unknown error'
                return Response({
                    "statusCode": status,
                    "body": json.dumps({'error': resp_body})
                }).with_security_headers()
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return Response({
                "statusCode": 400,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

    def generateDownloadLink(self, event, context):
        # This is a step function called from a state machine
        # Event type will always be "step-function"
        source_event = Event(event, context)
        data = source_event.parse()

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return False

            results = Results(target.name, self.s3_client, self.bucket, self.base_results_path)
            status, output, download_url = results.generateURL()
            if download_url:
                return {
                    'status': status,
                    'output': output,
                    'url': download_url
                }
            else:
                if status == 404:
                    message = 'No results found for target'
                else:
                    message = 'Unknown error'
                return {
                    'status': status,
                    'message': message
                }
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return False
