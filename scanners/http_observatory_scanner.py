import requests
import time
import os
import logging


class HTTPObservatoryScanner():

    def __init__(self, poll_interval=1, logger=logging.getLogger(__name__)):
        self.session = requests.Session()
        self.poll_interval = poll_interval
        self.api_url = os.getenv('HTTPOBS_API_URL')
        self.logger = logger

    def scan(self, hostname):
        # Initiate the scan
        if self.api_url[-1] != "/":
            analyze_url = self.api_url + '/analyze?host=' + hostname
        else:
            raise Exception("Invalid API URL specified for Observatory.")
        self.logger.info("Running HTTP Observatory scan on {}...".format(hostname))
        results = {}

        # Wait for the scan to complete, polling every second
        count = 0
        while count < 300:
            results['scan'] = self.session.post(analyze_url, data=None).json()
            # This means we got our results back, so return them!
            if results['scan']['status_code'] == 200 and results['scan']['state'] == "FINISHED" and results['scan']['grade'] is not None:
                break
            time.sleep(self.poll_interval)
            count += 1
        if count == 300:
            self.logger.warning(
                "Unable to get HTTP Observatory scan results within {} seconds, returning partial results.".format(count)
            )

        detail_url = self.api_url + '/getScanResults?scan=' + str(results['scan']['scan_id'])
        results['tests'] = self.session.get(detail_url).json()
        results['host'] = hostname
        return results
