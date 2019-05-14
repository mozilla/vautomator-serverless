import uuid
import logging
import boto3
import json
import os
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
                for scan_result in self.client.list_objects(Bucket=self.bucket_name, Prefix=target.name)['Contents']:
                    scan_output_list.append = str(scan_result['Key'])
                    # At this stage we know there are output files for the host
                    # Create a temp results directory to download them
                    # TODO: Call util function here in another try...except
            except Exception as e:
                # If we are here, there are no results for that host,
                # or the bucket name was wrong
                self.logger.warning("No scan output found in the bucket for: {}".format(target.name))
                return Response({
                    "statusCode": 404,
                    "body": json.dumps({'error': 'No results found for target'})
                }).with_security_headers()
            else:
                # Downloading output files to /tmp/<hostname> on the
                # "serverless" server, we should be OK to write to /tmp
                try:
                    for output in scan_output_list:
                        self.client.download_file(
                            self.bucket_name,
                            output,
                            SCAN_RESULTS_BASE_PATH + '/{}/{}'.format(target.name, output)
                        )
                except FileNotFoundError:
                    return Response({
                        "statusCode": 500,
                        "body": json.dumps({'OK': 'Scan output for {} downloaded to {}'.format(target.name, SCAN_RESULTS_BASE_PATH)})
                    }).with_security_headers()
                else:
                    # Downloaded the output for the target on the "serverless" server
                    # Now, we need to zip it up and return all
                    # TODO: Call the util function to zip it up
                    tgz_results = package_results(target.name + ".tar.gz", SCAN_RESULTS_BASE_PATH + "/" + target.name + "/" + output)
                    # Add to the Response class to return a content-type that is "tar.gz"
                    return Response({
                        "statusCode": 200,
                        "headers": {'X-Content-Type': 'application/gzip'},
                        "body": json.dumps({'OK': 'Scan output for {} downloaded to {}'.format(target.name, SCAN_RESULTS_BASE_PATH)}),
                        isBase64Encoded: True
                    }).with_security_headers()
        except ValueError:
            self.logger.error("Unrecognized payload")
            return Response({
                "statusCode": 500,
                "body": json.dumps({'error': 'Unrecognized payload'})
            }).with_security_headers()

        return
