import requests
import time
import os


class HTTPObservatoryScanner():

    def __init__(self, poll_interval=1):
        self.session = requests.Session()
        self.poll_interval = poll_interval
        self.api_url = os.getenv('HTTPOBS_API_URL')

    def scan(self, host):
        # Initiate the scan
        results = {}
        analyze_url = self.api_url + '/analyze?host=' + host.targetname
        results['scan'] = self.session.post(analyze_url, data=None).json()

        # Wait for the scan to complete, polling every second
        results['tests'] = self.__poll(results['scan']['scan_id'])
        results['host'] = host.targetname
        return results

    def __poll(self, scan_id):
        url = self.api_url + '/getScanResults?scan=' + str(scan_id)
        count = 0
        while count < 60:
            resp = self.session.get(url).json()
            # This means we got our results back, so return them!
            if 'content-security-policy' in resp:
                return resp

            time.sleep(self.poll_interval)
            count += 1
        raise Exception("Unable to get results within 60 seconds")