import json
import logging
import boto3
import os

from util.s3_helper import send_to_s3
from lib.target import Target
from scanners.httpobs_scanner import HTTPObservatoryScanner
from util.host_picker import Randomizer
from util.response import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runObsScanOnDemand(event, context):
    data = json.loads(event['body'])
    destination = Target(data.get('target'))

    if not destination.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(destination.targetname))
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'target was not valid or missing'})
         }).with_security_headers()

    print(SQS_CLIENT.send_message(
        QueueUrl=os.getenv('SQS_URL'),
        MessageBody=destination.targetname
    ))

    return Response({
        "statusCode": 200,
        "body": json.dumps({'OK': 'target added to the queue'})
    }).with_security_headers()


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
        scan_result = scanner.scan(destination.targetname)
        logger.info(scan_result)
        send_to_s3(destination.targetname, scan_result)


def runObsScanFromQ(event, context):

    # logger.info(event)
    # This is how we process the hostname
    
    for record, keys in event.items():
        for item in keys:
            if "body" in item:
                # print(item['body'])
                destination = item['body']
            else:
                logger.error("Target Validation Failed of: " +
                             json.dumps(destination))
                return False

    scanner = HTTPObservatoryScanner()
    scan_result = scanner.scan(destination)
    logger.info(scan_result)
    send_to_s3(destination, scan_result)
    return ''
