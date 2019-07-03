import logging
import requests
import json
import time
import os
import sys
import boto3
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

parser = argparse.ArgumentParser()
parser.add_argument(
    "--profile",
    help="Provide the AWS Profile from your boto configuration",
    default=os.environ.get("AWS_DEFAULT_PROFILE", None),
)
parser.add_argument("--region", help="Provide the AWS region manually", default="us-west-2")
parser.add_argument("fqdn", type=str, help="The target to scan")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

# Establish a session with that profile if given
session = boto3.Session(profile_name=args.profile)
# Programmatically obtain the API GW URL, and the REST API key
apigw_client = session.client("apigateway")
aws_response = apigw_client.get_api_keys(nameQuery="vautomator-serverless", includeValues=True)["items"][0]
rest_api_id, stage_name = "".join(aws_response["stageKeys"]).split("/")
gwapi_key = aws_response["value"]
API_GW_URL = "https://{}.execute-api.{}.amazonaws.com/".format(rest_api_id, session.region_name)

try:
    target = Target(args.fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(127)

scan_all_url = API_GW_URL + "{}/scan".format(stage_name)
session = requests.Session()
session.headers.update({"X-Api-Key": gwapi_key, "Content-Type": "application/json"})

logging.info("Sending POST to {}".format(scan_all_url))
response = session.post(scan_all_url, data='{"target":"' + target.name + '"}')
if response.status_code == 200 and 'executionArn' in response.json() and 'startDate' in response.json():
    logging.info("Triggered scan of: {}".format(target.name))

session.close()
time.sleep(2)
logging.info("Results will be emailed to your inbox when all scans run.")

# portscan_url = API_GW_URL + "{}/ondemand/portscan".format(stage_name)
# httpobs_scan_url = API_GW_URL + "{}/ondemand/httpobservatory".format(stage_name)
# tlsobs_scan_url = API_GW_URL + "{}/ondemand/tlsobservatory".format(stage_name)
# sshobs_scan_url = API_GW_URL + "{}/ondemand/sshobservatory".format(stage_name)
# tenableio_scan_url = API_GW_URL + "{}/ondemand/tenablescan".format(stage_name)
# direnum_scan_url = API_GW_URL + "{}/ondemand/direnum".format(stage_name)
# websearch_url = API_GW_URL + "{}/ondemand/websearch".format(stage_name)

# scan_types = {
#     'port': portscan_url,
#     'httpobservatory': httpobs_scan_url,
#     'tlsobservatory': tlsobs_scan_url,
#     'sshobservatory': sshobs_scan_url,
#     'websearch': websearch_url,
#     'tenable': tenableio_scan_url,
#     'direnum': direnum_scan_url
# }

# session = requests.Session()
# session.headers.update(
#     {
#         'X-Api-Key': gwapi_key,
#         'Content-Type': 'application/json'
#     }
# )
# for scan, scan_url in scan_types.items():
#     logging.info("Sending POST to {}".format(scan_url))
#     response = session.post(scan_url, data="{\"target\":\"" + target.name + "\"}")
#     if response.status_code == 200 and 'uuid' in response.json():
#         logging.info("Triggered a {} scan of: {}".format(scan, target.name))
#         time.sleep(1)

# session.close()
# time.sleep(2)
# logging.info(
#     "Scans kicked off for {}. Run \"download_results.py\" in 15 minutes to have the scan results.".format(target.name)
# )
