import logging
import sys
import requests
import os
import json
import time
from lib.target import Target

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want to scan: ")
# TODO: add relevant tasking call here to /ondemand/portscan
target = Target(fqdn)
if not target:
    logger.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(-1)

portscan_url = os.environ() + "/dev/ondemand/portscan"
httpobs_scan_url = os.environ() + "/dev/ondemand/httpobservatory"
tlsobs_scan_url = os.environ() + "/dev/ondemand/tlsobservatory"
sshobs_scan_url = os.environ() + "/dev/ondemand/sshobservatory"

session = requests.Session()
logger.info("Sending POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/portscan")
response = session.post(portscan_url, data='{"target":"{}"}'.format(target.name).json())
if response.status_code == 200 and 'uuid' in response.json():
    logger.info("Triggered a Port Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

# TODO: add relevant tasking call here to /ondemand/httpobservatory
logger.info("Sending POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/httpobservatory")
response = session.post(httpobs_scan_url, data='{"target":"{}"}'.format(target.name).json())
if response.status_code == 200 and 'uuid' in response.json():
    logger.info("Triggered an HTTP Observatory Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

# TODO: add relevant tasking call here to /ondemand/tlsobservatory
logger.info("Sending POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/tlsobservatory")
response = session.post(tlsobs_scan_url, data='{"target":"{}"}'.format(target.name).json())
if response.status_code == 200 and 'uuid' in response.json():
    logger.info("Triggered a TLS Observatory Scan of: {}".format(target.name))
    session.close()
time.sleep(1)

# TODO: add relevant tasking call here to /ondemand/sshobservatory
logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/sshobservatory")
response = session.post(sshobs_scan_url, data='{"target":"{}"}'.format(target.name).json())
if response.status_code == 200 and 'uuid' in response.json():
    logger.info("Triggered an SSH Observatory Scan of: {}".format(target.name))
    session.close()
