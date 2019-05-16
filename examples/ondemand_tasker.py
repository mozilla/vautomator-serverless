import logging
import requests
import json
import time
import os
import sys
import boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Can specify the profile/role in the code...
AWS_PROFILE = ""

if not AWS_PROFILE:
    try:
        # ...or read from an environment variable
        AWS_PROFILE = os.environ['AWS_PROFILE']
    except KeyError:
        logging.error("AWS profile not found. Either specify it as an environment variable"
                      " (AWS_PROFILE) or change the AWS_PROFILE variable in the code.")
        sys.exit(-1)

# Establish a session with that profile
session = boto3.Session(profile_name=AWS_PROFILE)
# Programmatically obtain the API GW URL, and the REST API key
apigw_client = session.client('apigateway')
aws_response = apigw_client.get_api_keys(
    nameQuery='vautomator-serverless',
    includeValues=True)['items'][0]
rest_api_id, stage_name = "".join(aws_response['stageKeys']).split('/')
gwapi_key = aws_response['value']
API_GW_URL = "https://{}.execute-api.{}.amazonaws.com/".format(rest_api_id, session.region_name)

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want to scan: ")
try:
    target = Target(fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(-2)

portscan_url = API_GW_URL + "{}/ondemand/portscan".format(stage_name)
httpobs_scan_url = API_GW_URL + "{}/ondemand/httpobservatory".format(stage_name)
tlsobs_scan_url = API_GW_URL + "{}/ondemand/tlsobservatory".format(stage_name)
sshobs_scan_url = API_GW_URL + "{}/ondemand/sshobservatory".format(stage_name)
tenableio_scan_url = API_GW_URL + "{}/ondemand/tenablescan".format(stage_name)
direnum_scan_url = API_GW_URL + "{}/ondemand/direnum".format(stage_name)
websearch_url = API_GW_URL + "{}/ondemand/websearch".format(stage_name)

scan_types = {
    'port': portscan_url,
    'httpobservatory': httpobs_scan_url,
    'tlsobservatory': tlsobs_scan_url,
    'sshobservatory': sshobs_scan_url,
    'websearch': websearch_url,
    'tenable': tenableio_scan_url,
    'direnum': direnum_scan_url
}

session = requests.Session()
session.headers.update(
    {
        'X-Api-Key': gwapi_key,
        'Content-Type': 'application/json'
    }
)
for scan, scan_url in scan_types.items():
    logging.info("Sending POST to {}".format(scan_url))
    response = session.post(scan_url, data="{\"target\":\"" + target.name + "\"}")
    if response.status_code == 200 and 'uuid' in response.json():
        logging.info("Triggered a {} scan of: {}".format(scan, target.name))
        time.sleep(1)

session.close()
time.sleep(2)
logging.info(
    "Scans kicked off for {}. Run \"download_results.py\" in 15 minutes to have the scan results.".format(target.name)
)
