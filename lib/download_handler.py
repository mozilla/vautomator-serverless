import uuid
import logging
import boto3
import json
import os
import base64
from lib.target import Target
from lib.response import Response
from lib.hosts import Hosts
from lib.utilities import package_results

S3_BUCKET = os.environ.get('S3_BUCKET')
SCAN_RESULTS_BASE_PATH = os.environ.get('SCAN_RESULTS_BASE_PATH')


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

            # Search S3 bucket for results matching the target host
            try:
                scan_output_list = []
                for scan_result in self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=target.name)['Contents']:
                    scan_output_list.append(str(scan_result['Key']))
            except Exception as e:
                # If we are here, there are no results for that host,
                # or the bucket name was wrong
                self.logger.warning("No scan output found in the bucket for: {}, exception: {}".format(target.name, e))
                return Response({
                    "statusCode": 404,
                    "body": json.dumps({'error': 'No results found for target'})
                }).with_security_headers()
            else:
                # At this stage we know there are output files for the host
                # Create a temp results directory to download them
                host_results_dir = os.path.join(SCAN_RESULTS_BASE_PATH, target.name)
                try:
                    if not os.path.exists(host_results_dir):
                        os.makedirs(host_results_dir)
                except PermissionError as e:
                    self.logger.error("Unable to store scan results at {}, exception: {}".format(host_results_dir, e))
                    return Response({
                        "statusCode": 500,
                        "body": json.dumps({'error': 'Unable to download scan results'})
                    }).with_security_headers()

                # Downloading output files to /tmp/<hostname> on the
                # "serverless" server, we should be OK to write to /tmp
                for output in scan_output_list:
                    self.s3_client.download_file(
                        self.bucket_name,
                        output,
                        host_results_dir + '/{}'.format(output)
                    )
                self.logger.info("Scan output for {} downloaded to {}".format(target.name, host_results_dir))
                # Downloaded the output for the target on the "serverless" server
                # Now, we need to zip it up and return
                tgz_results = package_results(host_results_dir)
                return Response({
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/gzip",
                        "Content-Disposition": "attachment; filename={}.tgz".format(target.name)
                    },
                    "body": base64.b64encode(tgz_results.getvalue()).decode("utf-8"),
                    "isBase64Encoded" : True
                }).with_security_headers()

        except ValueError:
            self.logger.error("Unrecognized payload")
            return Response({
                "statusCode": 500,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

        return
