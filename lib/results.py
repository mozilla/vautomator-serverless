import requests
import time
import os
import boto3
import logging
from lib.s3_helper import search_s3, download_s3, send_to_s3, create_presigned_url
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
        self.scan_output_dict = {
            'tcpscan': False,
            'tenablescan': False,
            'direnum': False,
            'sshobservatory': False,
            'httpobservatory': False,
            'tlsobservatory': False,
            'websearch': False
        }
        self.base_results_path = results_path
        self.logger = logger

    def download(self):
        # While downloading, let's just download whatever
        # results exist for a given host
        host_results_dir = os.path.join(self.base_results_path, self.hostname)
        self.scan_output_list, status = self.__poll()
        # status here is either 200, 202 or 404

        if self.scan_output_list and len(self.scan_output_list):
            # We have results, but we do not care how many
            ready = self.__prepareResults(host_results_dir)
            if ready:
                # Downloaded the output for the target on the "serverless" server
                # Now, we need to zip it up and return
                tgz_results = package_results(host_results_dir)
                return tgz_results, status
            else:
                # Error when preparing results, return 500
                return False, 500
        else:
            # No results found, return False
            return False, status

    def generateURL(self):
        # Generate a download URL for whichever results are in
        # the S3 bucket for that host, while keeping track of
        # missing results
        self.scan_output_dict, self.scan_output_list, status = self.__poll()
        if status == 404:
            return status, False, False
        else:
            # Does not matter if status is 200 or 202, we
            # will generate a signed URL, but also return
            # the result dictionary
            host_results_dir = os.path.join(self.base_results_path, self.hostname)
            ready = self.__prepareResults(host_results_dir)
            if ready:
                # Downloaded the output for the target on the "serverless" server
                # Now, we need to zip it up and upload back to S3.
                tgz_results = package_results(host_results_dir)
                s3_object = send_to_s3(self.hostname, tgz_results, client=self.s3_client, bucket=self.bucket)
                # We need to generate a signed URL now
                download_url = create_presigned_url(s3_object, client=self.s3_client, bucket=self.bucket)
                return status, self.scan_output_dict, download_url
            else:
                # Something went wrong, return False
                return status, False, False

    def __poll(self):
        # Search S3 bucket for results matching the target host
        try:
            self.scan_output_list = search_s3(self.hostname, self.s3_client, self.bucket)
        except Exception as e:
            # If we are here, there are no results for that host,
            # or the bucket name was wrong
            self.logger.warning("No scan output found in the bucket for: {}, exception: {}".format(self.hostname, e))
            return False, False, 404
        else:
            # At this stage we know there are scan output files for the host
            output_mapping = self.scan_output_dict.copy()
            for file in self.scan_output_list:
                hostname, output_type = file.split('_')
                del hostname
                for key, value in output_mapping.items():
                    if key in output_type:
                        output_mapping.update({key: True})

            if False in output_mapping.values():
                self.logger.warning("Not all scan output exists for {} ".format(self.hostname))
                return output_mapping, self.scan_output_list, 202
            else:
                return output_mapping, self.scan_output_list, 200

    def __prepareResults(self, host_results_dir):
        # Create a temp results directory to download them
        host_results_dir = os.path.join(self.base_results_path, self.hostname)
        try:
            if not os.path.exists(host_results_dir):
                os.makedirs(host_results_dir)
        except Exception as e:
            self.logger.error("Unable to store scan results at {}, exception: {}".format(host_results_dir, e))
            return False

        # Downloading output files to /tmp/<hostname> on the
        # "serverless" server, we should be OK to write to /tmp
        download_s3(self.scan_output_list, host_results_dir, self.s3_client, self.bucket)
        self.logger.info("Scan output for {} downloaded to {}".format(self.hostname, host_results_dir))
        return True
