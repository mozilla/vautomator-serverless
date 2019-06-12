import logging
import requests
import json
import time
import os
import sys
import boto3
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.target import Target
from lib.utilities import uppath

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

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want the results for: ")
try:
    target = Target(fqdn)
except AssertionError:
    logging.error("Target validation failed: target must be an FQDN or IPv4 only.")
    sys.exit(-2)

download_url = API_GW_URL + "{}/results".format(stage_name)

session = requests.Session()
session.headers.update(
    {
        'X-Api-Key': gwapi_key,
        'Accept': 'application/gzip',
        'Content-Type': 'application/json'
    }
)

logging.info("Sending POST to {}".format(download_url))
response = session.post(download_url, data="{\"target\":\"" + target.name + "\"}", stream=True)
if response.status_code == 200 or response.status_code == 202 and response.headers['Content-Type'] == "application/gzip":
    logging.info("Downloaded scan results for: {}, saving to disk...".format(target.name))
    time.sleep(1)
    with open(os.path.join(uppath(os.getcwd(), 1), "results/{}.tgz".format(target.name)), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        logging.info("Scan results for {} are saved in the results folder.".format(target.name))
else:
    logging.error("No results found for: {}".format(target.name))
del response

session.close()
