import requests
import time
import os
import logging


class SSHObservatoryScanner():

    def __init__(self, poll_interval=1, logger=logging.getLogger(__name__)):
        self.session = requests.Session()
        self.poll_interval = poll_interval
        self.api_url = os.getenv('SSHOBS_API_URL')

    def scan(self, hostname):
        # Initiate the scan
        if self.api_url[-1] != "/":
            analyze_url = self.api_url + '/scan?target=' + hostname
            results = {}
            response = self.session.post(analyze_url, data=None).json()
            print(response.content)
            scan_id = self.session.post(analyze_url, data=None).json()['uuid']

            # Wait for the scan to complete, polling every second
            results['scan'] = self.__poll(scan_id)
            results['host'] = hostname
            return results
        else:
            raise Exception("Invalid API URL specified for Observatory.")

    def __poll(self, scan_id):
        url = self.api_url + '/scan/results?uuid=' + str(scan_id)
        count = 0
        while count < 60:
            resp = self.session.get(url).json()
            # This means we got our results back, so return them!
            if 'ssh_scan_version' in resp:
                return resp

            time.sleep(self.poll_interval)
            count += 1
        raise Exception("Unable to get results within 60 seconds")
