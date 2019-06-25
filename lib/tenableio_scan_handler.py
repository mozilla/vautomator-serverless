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


class TIOScanHandler(object):
    def __init__(
        self, sqs_client=boto3.client('sqs', region_name='us-west-2'),
        queueURL=os.getenv('SQS_URL'),
        logger=logging.getLogger(__name__),
        region='us-west-2'
    ):
        self.sqs_client = sqs_client
        self.queueURL = queueURL
        self.logger = logger
        self.region = region

    def queue(self, event, context):
        # print("Event: {}, context: {}".format(event, context.invoked_function_arn))
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
            scanner_ref = scanner.scan(target)
            if scanner_ref:
                scanner_ref.launch(wait=False)
            return scanner_ref
        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return False

    def pollScanResults(self, event, context):
        # This function will take a Tenable.io ScanRef object, and
        # query Tenable.io API for the status of that scan, and
        # if completed, return the results a HTML or JSON object

        scan_ref = event['responses']['Tenablescan']
        scanner = TIOScanner(logger=self.logger)
        result = scanner.scanResult(scan_ref)

        return result
