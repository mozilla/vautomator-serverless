import logging
import requests
import json
import time
import os
import sys
import boto3
import argparse
import getpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--profile",
    help="Provide the AWS Profile from your boto configuration",
    default=os.environ.get("AWS_DEFAULT_PROFILE", None),
)
parser.add_argument("--region", help="Provide the AWS region manually", default="us-west-2")
parser.add_argument("fqdn", type=str, help="The target to scan")
args = parser.parse_args()

if args.profile:
    # Establish a session with that profile if given
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    # Programmatically obtain the REST API key
    apigw_client = session.client("apigateway")
    aws_response = apigw_client.get_api_keys(nameQuery="vautomator-serverless", includeValues=True)["items"][0]
    rest_api_id, stage_name = "".join(aws_response["stageKeys"]).split("/")
    gwapi_key = aws_response["value"]
else:
    # Prompt the user for the API key
    gwapi_key = getpass.getpass(prompt='API key: ')

# We are now using a custom domain to host the API
custom_domain = "vautomator.security.allizom.org"

try:
    target = Target(args.fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(127)

# Using the REST endpoint exposed by the step function
scan_all_url = "https://{}".format(custom_domain) + "/api/scan"
session = requests.Session()
session.headers.update({"X-Api-Key": gwapi_key, "Content-Type": "application/json"})

logging.info("Sending POST to {}".format(scan_all_url))
response = session.post(scan_all_url, data='{"target":"' + target.name + '"}')
if response.status_code == 200 and 'executionArn' in response.json() and 'startDate' in response.json():
    logging.info("Triggered scan of: {}".format(target.name))
    time.sleep(1)
    logging.info("Results will be emailed to your inbox when all scans run.")
elif response.status_code == 403:
    logging.error("Invalid API key.")
else:
    logging.error("Something went wrong. Ensure you have the correct API key and the service is operational.")

session.close()
