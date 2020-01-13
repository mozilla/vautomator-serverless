import logging
import certstream
import requests
import json
import time
import os
import sys
import boto3
import argparse
import getpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# This is an example of a long-running service/process which will monitor for
# CT Logs in real-time and as soon as a certificat_update action is triggered
# for a domain pattern we care about, we will immediately take action to task
# port scans and observatory scans by calling our public REST API endpoints

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
# Using the REST endpoint exposed by the step function
scan_all_url = "https://{}".format(custom_domain) + "/api/scan"


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
                    session.headers.update({"X-Api-Key": gwapi_key, "Content-Type": "application/json"})
                    logging.info("Sending POST to {}".format(scan_all_url))
                    response = session.post(scan_all_url, data='{"target":"' + fqdn + '"}')
                    if response.status_code == 200 and 'executionArn' in response.json() and 'startDate' in response.json():
                        logging.info("Triggered scan of: {}".format(fqdn))
                        time.sleep(1)
                        logging.info("Results will be emailed to your inbox when all scans run.")
                    elif response.status_code == 403:
                        logging.error("Invalid API key.")
                        sys.exit(127)
                    else:
                        logging.error("Something went wrong. Ensure you have the correct API key and the service is operational.")
                        sys.exit(127)
                    session.close()
                    

certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
