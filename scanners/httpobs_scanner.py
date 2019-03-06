import requests
import time


class HTTPObservatoryScanner():
    ## TODO: Re-write this with the httpobs python module
    def __init__(self, sleep_interval=1):
        self.session = requests.Session()
        self.sleep_interval = sleep_interval
        self.api_url = 'https://http-observatory.security.mozilla.org/api/v1'

    def scan(self, host):
        # Initiate the scan
        results = {}
        analyze_url = self.api_url + '/analyze?host=' + host
        results['scan'] = self.session.post(analyze_url, data=None).json()

        # Wait for the scan to complete, polling every second
        results['tests'] = self.__poll(results['scan']['scan_id'])
        results['host'] = host
        return results

    def __poll(self, scan_id):
        url = self.api_url + '/getScanResults?scan=' + str(scan_id)
        count = 0
        while count < 60:
            resp = self.session.get(url).json()
            # This means we got our results back, so return them!
            if 'content-security-policy' in resp:
                return resp

            time.sleep(self.sleep_interval)
            count += 1
        raise Exception("Unable to get results within 60 seconds")