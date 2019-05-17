import requests
import time
import os
import boto3
import logging
from lib.s3_helper import search_s3, download_s3
from lib.utilities import package_results

S3_BUCKET = os.environ.get('S3_BUCKET')
SCAN_RESULTS_BASE_PATH = os.environ.get('SCAN_RESULTS_BASE_PATH')


class Results(object):
    def __init__(
        self,
        hostname,
        s3_client=boto3.client('s3'),
        bucket=S3_BUCKET,
        results_path=SCAN_RESULTS_BASE_PATH,
        logger=logging.getLogger(__name__)
    ):
        self.hostname = hostname
        self.s3_client = s3_client
        self.bucket = bucket
        self.scan_output_list = []
        self.base_results_path = results_path
        self.logger = logger

    def download(self):
        host_results_dir = os.path.join(self.base_results_path, self.hostname)
        ready, status = self.__prepareResults(host_results_dir)
        if ready:
            # Downloaded the output for the target on the "serverless" server
            # Now, we need to zip it up and return
            tgz_results = package_results(host_results_dir)
            return tgz_results, status
        else:
            # Something went wrong, return False
            return False, status

    def generateURL(self):
        host_results_dir = os.path.join(self.base_results_path, self.hostname)
        ready, status = self.__prepareResults(host_results_dir)
        if ready:
            # Downloaded the output for the target on the "serverless" server
            # Now, we need to zip it up, save to disk and upload back to S3.
            tgz_results = package_results(host_results_dir, self.base_results_path)
            return tgz_results, status
        else:
            # Something went wrong, return False
            return False, status

    def __prepareResults(self, host_results_dir):
        # Search S3 bucket for results matching the target host
        try:
            self.scan_output_list = search_s3(self.hostname, self.s3_client, self.bucket)
        except Exception as e:
            # If we are here, there are no results for that host,
            # or the bucket name was wrong
            self.logger.warning("No scan output found in the bucket for: {}, exception: {}".format(self.hostname, e))
            return False, 404
        else:
            # At this stage we know there are output files for the host
            # Create a temp results directory to download them
            host_results_dir = os.path.join(self.base_results_path, self.hostname)
            try:
                if not os.path.exists(host_results_dir):
                    os.makedirs(host_results_dir)
            except Exception as e:
                self.logger.error("Unable to store scan results at {}, exception: {}".format(host_results_dir, e))
                return False, 500

            # Downloading output files to /tmp/<hostname> on the
            # "serverless" server, we should be OK to write to /tmp
            download_s3(self.scan_output_list, host_results_dir, self.s3_client, self.bucket)
            self.logger.info("Scan output for {} downloaded to {}".format(self.hostname, host_results_dir))
            return True, 200
