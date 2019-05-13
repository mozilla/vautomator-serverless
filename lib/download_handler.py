import uuid
import logging
import boto3
import json
import os
from lib.target import Target
from lib.response import Response
from lib.hosts import Hosts

S3_BUCKET = os.environ.get('S3_BUCKET')


class DownloadHandler(object):
    def __init__(self, s3_client=boto3.client('s3'), bucket_name=S3_BUCKET, logger=logging.getLogger(__name__), region='us-west-2'):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.logger = logger
        self.region = region

    def downloadResults(self, event, context):
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

            # S3 search here
            self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=target.name)['Contents']
            # Zip it up before returning (util function)
            # Add a new response type (for tar.gz)


            # Use a UUID for the scan type and return it
            return Response({
                "statusCode": 200,
                "body": json.dumps({'uuid': scan_uuid})
            }).with_security_headers()
        except ValueError:
            self.logger.error("Unrecognized payload")
            return Response({
                "statusCode": 500,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

        return
