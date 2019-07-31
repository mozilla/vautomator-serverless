import logging
import requests
import json
import time
import os
import sys
import boto3
import shutil
import tarfile
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target
from lib.utilities import uppath

# Use this as a client to download scan results for a given host.

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--profile",
    help="Provide the AWS Profile from your boto configuration",
    default=os.environ.get("AWS_DEFAULT_PROFILE", None),
)
parser.add_argument("--region", help="Provide the AWS region manually", default="us-west-2")
parser.add_argument("fqdn", type=str, help="The target to scan")
parser.add_argument("-x", "--extract", help="Auto extract results", action="store_true")
parser.add_argument("--results", help="Specify a results directory", default=os.path.join(os.getcwd(), "results/"))
args = parser.parse_args()

# Establish a session with that profile if given
session = boto3.Session(profile_name=args.profile, region_name=args.region)
# Programmatically obtain the REST API key
apigw_client = session.client("apigateway")
aws_response = apigw_client.get_api_keys(nameQuery="vautomator-serverless", includeValues=True)["items"][0]
rest_api_id, stage_name = "".join(aws_response["stageKeys"]).split("/")
gwapi_key = aws_response["value"]
# We are now using a custom domain to host the API
custom_domain = "vautomator.security.allizom.org"

try:
    target = Target(args.fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(127)

download_url = "https://{}".format(custom_domain) + "/api/results"
session = requests.Session()
session.headers.update({"X-Api-Key": gwapi_key, "Accept": "application/gzip", "Content-Type": "application/json"})

logging.info("Sending POST to {}".format(download_url))
response = session.post(download_url, data='{"target":"' + target.name + '"}', stream=True)
if (
    response.status_code == 200
    or response.status_code == 202
    and response.headers["Content-Type"] == "application/gzip"
):
    logging.info("Downloaded scan results for: {}, saving to disk...".format(target.name))
    dirpath = args.results
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    path = os.path.join(dirpath, "{}.tar.gz".format(target.name))
    with open(path, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
        logging.info("Scan results for {} are saved in the results folder.".format(target.name))
    if response.status_code == 202:
        logging.warning("Not all scan results exist for the target. You should run the failed scans manually.")

    if args.extract:
        tdirpath = os.path.join(dirpath, "{}/".format(target.name))
        if not os.path.isdir(dirpath):
            os.mkdir(tdirpath)
        with tarfile.open(path) as tar:
            tar.extractall(path=tdirpath)
            logging.info("Scan results for {} are extracted in the results folder.".format(target.name))
else:
    logging.error("No results found for: {}".format(target.name))

del response
session.close()
