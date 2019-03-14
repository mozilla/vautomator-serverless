import os
import requests
import re


class CTLogs():

    def __init__(self, poll_interval=1):
        self._url = os.getenv('CERTSTREAM_URL')
        self.session = requests.Session()

    def latest25(self):
        if self._url[-1] != "/":
            latest_url = self._url + '/latest.json'
        else:
            raise Exception("Invalid URL specified for certstream.")

        latest_certs = self.session.get(latest_url).json()
        most_recent_domains = []
        target_domain_patterns = []
        compiled_patterns = []
        for message in latest_certs['messages']:
            if message['message_type'] == "certificate_update":
                for domain in message['data']['leaf_cert']['all_domains']:
                    most_recent_domains.append(domain)
        
        target_domain_patterns = [
                '.*\.mozilla\.com.*',
                ".*\.mozilla\.org.*",
                ".*\.firefox\.com.*",
            ]
        for pattern in target_domain_patterns:
            compiled_patterns.append(re.compile(pattern))
        
        modified_domains = [domain for domain in most_recent_domains
                            if any(regex.match(domain) for regex in
                                   compiled_patterns)]
        return modified_domains
