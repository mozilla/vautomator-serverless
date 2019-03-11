import json
import logging
import boto3
import os

from util.s3_helper import send_to_s3
from util.validator import validateTarget
from lib.target import Target
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from util.randomizer import Randomizer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runScheduledObservatoryScan(event, context):

    # For demo purposes, we will use a static list here
    target_list = [
        "www.mozilla.org",
        "infosec.mozilla.org",
    ]
    randomizer = Randomizer(target_list)
    target = validateTarget(randomizer.next())
    if target:
        logger.info("Tasking Observatory Scan of: " +
                    json.dumps(target.targetname))
        scanner = HTTPObservatoryScanner()
        scan_result = scanner.scan(target)
        logger.info("Completed Observatory Scan of " +
                    json.dumps(target.targetname))
        send_to_s3(target.targetname, scan_result)
    else:
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))


def runObservatoryScanFromQ(event, context):

    # This is how we process the hostname
    # Demonstration purposes, in the final example 
    # we should extract the hostname and perform a scan

    for record, keys in event.items():
        for item in keys:
            if "body" in item:
                logger.info(item['body'])
    return ''


def putInQueue(event, context):
    # For demo purposes, this function is invoked manually
    # Also for demo purposes, we will use a static list here
    # We need to figure out a way to put stuff in the queue regularly
    target_list = [
        "www.mozilla.org",
        "infosec.mozilla.org",
    ]
    randomizer = Randomizer(target_list)
    target = Target(randomizer.next())

    print(SQS_CLIENT.send_message(
        QueueUrl=os.getenv('SQS_URL'),
        MessageBody=target.targetname
    ))
    return ''
