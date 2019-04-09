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
# API_GW_URL = "https://y2ippncfd1.execute-api.us-west-2.amazonaws.com"
API_GW_URL = os.environ['API_GW_URL']

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

session = requests.Session()
logging.info("Sending POST to {}".format(portscan_url))
response = session.post(portscan_url, data="{\"target\":\"" + target.name + "\"}")
if response.status_code == 200 and 'uuid' in response.json():
    logging.info("Triggered a Port Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

logging.info("Sending POST to {}".format(httpobs_scan_url))
response = session.post(httpobs_scan_url, data="{\"target\":\"" + target.name + "\"}")
if response.status_code == 200 and 'uuid' in response.json():
    logging.info("Triggered an HTTP Observatory Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

logging.info("Sending POST to {}".format(tlsobs_scan_url))
response = session.post(tlsobs_scan_url, data="{\"target\":\"" + target.name + "\"}")
if response.status_code == 200 and 'uuid' in response.json():
    logging.info("Triggered a TLS Observatory Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

logging.info("Sending POST to {}".format(sshobs_scan_url))
response = session.post(sshobs_scan_url, data="{\"target\":\"" + target.name + "\"}")
if response.status_code == 200 and 'uuid' in response.json():
    logging.info("Triggered an SSH Observatory Scan of: {}".format(target.name))
    session.close()
