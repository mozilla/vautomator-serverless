import json
import datetime
import logging

from util.s3_helper import send_to_s3
from lib.target import Target
from scanners.httpobs_scanner import HTTPObservatoryScanner
from util.host_picker import Randomizer
from util.response import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def runObsScan(event, context):

    # Test out S3 upload capability
    url = 'https://raw.githubusercontent.com/mozilla/vautomator-serverless/scheduled-scans/hostlist.json'
    randomizer = Randomizer(url)
    scanner = HTTPObservatoryScanner()
    destination = Target(randomizer.next())
    # Need to perform target validation here

    if not destination.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(destination.targetname))
    else:
        scan_result = scanner.scan(destination)
        logger.info(scan_result)
        send_to_s3(destination.targetname, scan_result)
