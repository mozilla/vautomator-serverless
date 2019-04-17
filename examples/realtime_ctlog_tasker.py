import logging
import certstream
import requests
import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# This is an example of a long-running service/process which will monitor for
# CT Logs in real-time and as soon as a certificat_update action is triggered
# for a domain pattern we care about, we will immediately take action to task
# port scans and observatory scans by calling our public REST API endpoints

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

try:
    API_GW_URL = os.environ['API_GW_URL']
except KeyError:
    API_GW_URL = "https://y2ippncfd1.execute-api.us-west-2.amazonaws.com"

portscan_url = API_GW_URL + "/dev/ondemand/portscan"
httpobs_scan_url = API_GW_URL + "/dev/ondemand/httpobservatory"
tlsobs_scan_url = API_GW_URL + "/dev/ondemand/tlsobservatory"
sshobs_scan_url = API_GW_URL + "/dev/ondemand/sshobservatory"
tenableio_scan_url = API_GW_URL + "/dev/ondemand/tenablescan"

scan_types = {
    "port": portscan_url,
    "httpobservatory": httpobs_scan_url,
    "tlsobservatory": tlsobs_scan_url,
    "sshobservatory": sshobs_scan_url,
    "tenable": tenableio_scan_url
}


def print_callback(message, context):
    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        domain_patterns = [
            ".mozilla.com",
            ".mozilla.org",
            ".firefox.com",
        ]

        for fqdn in all_domains:
            for domain_pattern in domain_patterns:
                # We want all legit FDQNs, but we can't scan wild-cards
                if fqdn.endswith(domain_pattern) and ('*' not in fqdn):

                    session = requests.Session()
                    for scan, scan_url in scan_types.items():
                        logging.info("Sending POST to {}".format(scan_url))
                        response = session.post(scan_url, data="{\"target\":\"" + fqdn + "\"}")
                        if response.status_code == 200 and 'uuid' in response.json():
                            logging.info("Triggered a {} scan of: {}".format(scan, fqdn))
                            time.sleep(1)
                    session.close()


certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
