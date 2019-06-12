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
SCAN_RESULTS_BASE_PATH = os.environ.get('SCAN_RESULTS_BASE_PATH')


class ResultsHandler(object):
    def __init__(
        self,
        s3_client=boto3.client('s3'),
        bucket=S3_BUCKET,
        logger=logging.getLogger(__name__),
        region='us-west-2',
        results_path=SCAN_RESULTS_BASE_PATH
    ):
        self.s3_client = s3_client
        self.bucket = bucket
        self.logger = logger
        self.region = region
        self.base_results_path = results_path

    def getResults(self, event, context):
        # print("Event: {}, context: {}".format(event, context))
        source_event = Event(event, context)
        data = source_event.parse()
        print(source_event.type)

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return Response({
                    "statusCode": 400,
                    "body": json.dumps({'error': 'Target was not valid or missing'})
                }).with_security_headers()

            results = Results(target.name, self.s3_client, self.bucket, self.base_results_path)
            if source_event.type == "step-function":
                # Use generateURL route
                download_url, status = results.generateDownloadURL()
                if download_url:
                    return Response({
                        "statusCode": status,
                        "body": json.dumps({'url': download_url})
                    }).with_security_headers()
                else:
                    if status == 404:
                        resp_body = 'No results found for target'
                    else:
                        resp_body = 'Unknown error'
                    return Response({
                        "statusCode": status,
                        "body": json.dumps({'error': resp_body})
                    }).with_security_headers()
            else:
                # Use download route
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
