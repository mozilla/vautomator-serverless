import uuid
import logging
import boto3
import json
import os
from lib.target import Target
from lib.response import Response
from lib.hosts import Hosts
from lib.event import Event
from scanners.tenable_io_scanner import TIOScanner
from lib.s3_helper import send_to_s3

REGION = os.getenv('REGION', 'us-west-2')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_CLIENT = boto3.client('s3', region_name=REGION)


class TIOScanHandler(object):
    def __init__(
        self, sqs_client=boto3.client('sqs', region_name=REGION),
        queueURL=os.getenv('SQS_URL'),
        s3_client=S3_CLIENT,
        bucket=S3_BUCKET,
        logger=logging.getLogger(__name__),
    ):
        self.sqs_client = sqs_client
        self.queueURL = queueURL
        self.s3_client = s3_client
        self.s3_bucket = bucket
        self.logger = logger

    def queue(self, event, context):
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

            scan_uuid = str(uuid.uuid4())
            self.sqs_client.send_message(
                QueueUrl=self.queueURL,
                MessageBody="tenableio|" + target.name
                + "|" + scan_uuid
            )

            # Use a UUID for the scan type and return it
            return Response({
                "statusCode": 200,
                "body": json.dumps({'uuid': scan_uuid})
            }).with_security_headers()
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return Response({
                "statusCode": 400,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

    def runFromStepFunction(self, event, context):
        source_event = Event(event, context)
        data = source_event.parse()

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return False

            # Run the scan here and return the ScanRef object
            scanner = TIOScanner(logger=self.logger)
            scanner_ref = scanner.scan(target.name)
            if scanner_ref:
                scanner_ref.launch(wait=False)
                return {'id': scanner_ref.id}
            else:
                return False
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return False

    def pollScanResults(self, event, context):
        # This function will take a Tenable.io scan ID, and
        # query Tenable.io API for the status of that scan, and
        # if completed, return the results a JSON object

        source_event = Event(event, context)
        data = source_event.parse()

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return False

            scanID = event['responses']['Tenablescan']['id']
            scanner = TIOScanner(logger=self.logger)
            json_result = scanner.scanResult(scanID, result_format="json")
            html_result = scanner.scanResult(scanID, result_format="html")
            if json_result and html_result:
                send_to_s3(target.name + "_tenablescan", json_result, client=self.s3_client, bucket=self.s3_bucket)
                send_to_s3(target.name + "_tenablescan", html_result, client=self.s3_client, bucket=self.s3_bucket)
                return {'statusCode': 200}
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return False
