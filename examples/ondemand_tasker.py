import logging
import requests
import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
try:
    API_GW_URL = os.environ['API_GW_URL']
except KeyError:
    API_GW_URL = "https://y2ippncfd1.execute-api.us-west-2.amazonaws.com"

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want to scan: ")
try:
    target = Target(fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(-1)

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

session = requests.Session()
for scan, scan_url in scan_types.items():
    logging.info("Sending POST to {}".format(scan_url))
    response = session.post(scan_url, data="{\"target\":\"" + target.name + "\"}")
    if response.status_code == 200 and 'uuid' in response.json():
        logging.info("Triggered a {} scan of: {}".format(scan, target.name))
        time.sleep(1)

session.close()
