import uuid
import logging
import boto3
import json
import os

from lib.target import Target
from lib.response import Response
from lib.hosts import Hosts


class PortScanHandler(object):
    def __init__(self, sqs_client=boto3.client('sqs', region_name='us-west-2'), logger=logging.getLogger(__name__), region='us-west-2'):
        self.sqs_client = sqs_client
        self.logger = logger
        self.region = region

    def queue(self, event, context):
        data = json.loads(event['body'])
        if "target" not in data:
            self.logger.error("Unrecognized payload")
            return Response({
                "statusCode": 500,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

        target = Target(data.get('target'))
        if not target:
            self.logger.error("Target validation failed of: " +
                              target.name)
            return Response({
                "statusCode": 400,
                "body": json.dumps({'error': 'Target was not valid or missing'})
            }).with_security_headers()

        scan_uuid = str(uuid.uuid4())
        print(self.sqs_client.send_message(
            QueueUrl=os.getenv('SQS_URL'),
            MessageBody="portscan|" + target.name
            + "|" + scan_uuid
        ))

        # Use a UUID for the scan type and return it
        return Response({
            "statusCode": 200,
            "body": json.dumps({'uuid': scan_uuid})
        }).with_security_headers()

    def queue_scheduled(self, event, context):
        hosts = Hosts()
        hostname_list = hosts.getList()
        for hostname in hostname_list:
            self.sqs_client.send_message(
                QueueUrl=os.getenv('SQS_URL'),
                DelaySeconds=2,
                MessageBody="portscan|" + hostname
                + "|"
            )
            self.logger.info("Tasking port scan of: " + hostname)

        self.logger.info("Host list has been added to the queue for port scan.")
