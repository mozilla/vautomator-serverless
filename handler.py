import json
import logging
import boto3
import os

from util.s3_helper import send_to_s3
from util.validator import validateTarget
from lib.target import Target
from scanners.httpobs_scanner import HTTPObservatoryScanner
from scanners.port_scanner import PortScanner
from util.randomizer import Randomizer
from util.response import Response
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from util.randomizer import Randomizer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runRegularPortScan(event, context):
    url = 'https://raw.githubusercontent.com/mozilla/vautomator-serverless/scheduled-scans/hostlist.json'
    randomizer = Randomizer(url)
    target = Target(randomizer.next())

    if not target.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))

    scanner = PortScanner()
    results = scanner.scanAll(target.targetname)
    logger.info(results)
    send_to_s3(target.targetname + "-portscan", results)


def putInQueueFromAPIGateway(event, context):
    data = json.loads(event['body'])
    target = Target(data.get('target'))

    if not target.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'target was not valid or missing'})
         }).with_security_headers()

    print(SQS_CLIENT.send_message(
        QueueUrl=os.getenv('SQS_URL'),
        MessageBody=target.targetname
    ))

    return Response({
        "statusCode": 200,
        "body": json.dumps({'OK': 'target added to the queue'})
    }).with_security_headers()


def runRegularObsScan(event, context):

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
        scan_result = scanner.scan(target.targetname)
        logger.info(scan_result)
        send_to_s3(target.targetname, scan_result)


def runObsScanFromQ(event, context):
    
    for record, keys in event.items():
        for item in keys:
            if "body" in item:
                # print(item['body'])
                target = item['body']
            else:
                logger.error("Target Validation Failed of: " +
                             json.dumps(target))
                return False

    scanner = HTTPObservatoryScanner()
    scan_result = scanner.scan(target)
    logger.info(scan_result)
    send_to_s3(target, scan_result)
    return ''


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
