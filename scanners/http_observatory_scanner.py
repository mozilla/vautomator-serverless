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
        results['scan'] = self.session.post(analyze_url, data=None).json()

        # Wait for the scan to complete, polling every second
        results['tests'] = self.__poll(results['scan']['scan_id'])
        results['host'] = hostname
        return results

    def __poll(self, scan_id):
        url = self.api_url + '/getScanResults?scan=' + str(scan_id)
        count = 0
        while count < 300:
            resp = self.session.get(url).json()
            # This means we got our results back, so return them!
            if 'content-security-policy' in resp:
                return resp

            time.sleep(self.poll_interval)
            count += 1
        raise Exception("Unable to get results within {} seconds".format(count))
