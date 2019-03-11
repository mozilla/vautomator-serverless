import json
import datetime
import logging
import boto3
import os

from util.s3_helper import send_to_s3
from lib.target import Target
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from util.randomizer import Randomizer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runObsScan(event, context):

    # Test out S3 upload capability
    url = 'https://raw.githubusercontent.com/mozilla/vautomator-serverless/scheduled-scans/hostlist.json'
    randomizer = Randomizer(url)
    scanner = HTTPObservatoryScanner()
    target = Target(randomizer.next())
    # Need to perform target validation here

    if not target.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))
    else:
        logger.info("Tasking Observatory Scan of: " +
                    json.dumps(target.targetname))
        scan_result = scanner.scan(target)
        logger.info("Completed Observatory Scan of " +
                    json.dumps(target.targetname))
        send_to_s3(target.targetname, scan_result)
