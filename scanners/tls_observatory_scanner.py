import requests
import time
import os


class TLSObservatoryScanner():

    def __init__(self, poll_interval=1):
        self.session = requests.Session()
        self.poll_interval = poll_interval
        self.api_url = os.getenv('TLSOBS_API_URL')

    def scan(self, hostname):
        # Initiate the scan
        if self.api_url[-1] != "/":
            scan_url = self.api_url + '/scan?target=' + hostname
        else:
            raise Exception("Invalid API URL specified for TLS Observatory.")
        results = {}
        scan_id = self.session.post(scan_url, data=None).json()['scan_id']

        # Wait for the scan to complete,
        # polling until completion percentage is 100
        results['scan'] = self.__poll(scan_id)
        results['host'] = hostname
        return results

    def __poll(self, scan_id):
        url = self.api_url + '/results?id=' + str(scan_id)
        completion_percentage = 0
        while completion_percentage != 100:
            resp = self.session.get(url)
            # This means we got our results back, so return them!
            if resp.status_code == 200 and resp.json()['completion_perc'] == 100:
                return resp.json()

            time.sleep(self.poll_interval)
            completion_percentage = resp['completion_perc']
        raise Exception("Unable to get results from TLS observatory API.")
