import json
import datetime
import logging

from util.s3_helper import send_to_s3

from scanners.httpobs_scanner import HTTPObservatoryScanner
from util.host_picker import Randomizer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def run(event, context):
    # Test out S3 upload capability
    url = 'https://raw.githubusercontent.com/mozilla/http-observatory-dashboard/master/httpobsdashboard/conf/sites.json'
    randomizer = Randomizer(url)
    scanner = HTTPObservatoryScanner()
    hostname = randomizer.next()
    scan_result = scanner.scan(hostname)
    logger.info(scan_result)
    send_to_s3(hostname, scan_result)
