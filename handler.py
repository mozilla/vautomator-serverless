import json
import logging
import boto3
import os
import uuid

from util.s3_helper import send_to_s3
from lib.target import Target
from scanners.port_scanner import PortScanner
from util.response import Response
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from util.randomizer import Randomizer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def addPortScanToQueue(event, context):
    data = json.loads(event['body'])
    if "target" not in data:
        logger.error("Unrecognized payload")
        return Response({
             "statusCode": 500,
             "body": json.dumps({'error': 'Unrecognized payload'})
         }).with_security_headers()
    
    target = Target(data.get('target'))
    if target.isValid():
        scan_uuid = str(uuid.uuid4())
        print(SQS_CLIENT.send_message(
              QueueUrl=os.getenv('SQS_URL'),
              MessageBody="portscan|" + target.targetname
              + "|" + scan_uuid
              ))

        # Use a UUID for the scan type and return it 
        return Response({
            "statusCode": 200,
            "body": json.dumps({'uuid': scan_uuid})
        }).with_security_headers()

    else:
        logger.error("Target validation failed of: " +
                     target.targetname)
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'Target was not valid or missing'})
         }).with_security_headers()


def runScheduledPortScan(event, context):
    # This is needed for nmap static library to be added to the path
    original_pathvar = os.environ['PATH']
    os.environ['PATH'] = original_pathvar \
        + ':' + os.environ['LAMBDA_TASK_ROOT'] \
        + '/bin/nmap-standalone/'

    # For demo purposes, we will use a static list here
    target_list = [
        "www.mozilla.org",
        "infosec.mozilla.org",
    ]
    randomizer = Randomizer(target_list)
    target = Target(randomizer.next())

    if target.isValid():
        logger.info("Tasking port scan of: " +
                    target.targetname)
        scanner = PortScanner()
        results = scanner.scanTCP(target.targetname)
        logger.info("Completed port scan of " +
                    target.targetname)
        send_to_s3(target.targetname + "_tcpscan", results)
    else:
        logger.error("Target validation failed of: " +
                     target.targetname)
    
    os.environ['PATH'] = original_pathvar


def addObservatoryScanToQueue(event, context):
    data = json.loads(event['body'])
    if "target" not in data:
        logger.error("Unrecognized payload")
        return Response({
             "statusCode": 500,
             "body": json.dumps({'error': 'Unrecognized payload'})
         }).with_security_headers()

    target = Target(data.get('target'))
    if target.isValid():
        scan_uuid = str(uuid.uuid4())
        print(SQS_CLIENT.send_message(
              QueueUrl=os.getenv('SQS_URL'),
              MessageBody="observatory|" + target.targetname
              + "|" + scan_uuid
              ))
        return Response({
            "statusCode": 200,
            "body": json.dumps({'uuid': scan_uuid})
        }).with_security_headers()
    
    else:
        logger.error("Target validation failed of: " +
                     target.targetname)
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'Target was not valid or missing'})
         }).with_security_headers()


def runScanFromQ(event, context):
    
    # This is needed for nmap static library to be added to the path
    original_pathvar = os.environ['PATH']
    os.environ['PATH'] = original_pathvar \
        + ':' + os.environ['LAMBDA_TASK_ROOT'] \
        + '/bin/nmap-standalone/'
    
    # Read the queue
    for record, keys in event.items():
        for item in keys:
            if "body" in item:
                message = item['body']
                scan_type, target, uuid = message.split('|')
                if scan_type == "observatory":
                    scanner = HTTPObservatoryScanner()
                    scan_result = scanner.scan(target)
                    send_to_s3(target + "_observatory", scan_result)
                elif scan_type == "portscan":
                    scanner = PortScanner()
                    scan_result = scanner.scanTCP(target)
                    send_to_s3(target + "_tcpscan", scan_result)
                else:
                    # Manually invoked, just log the message
                    logger.info("Message in queue: " +
                                message)
            else:
                logger.error("Unrecognized message in queue: " +
                             message)
    
    os.environ['PATH'] = original_pathvar


def runScheduledObservatoryScan(event, context):

    # For demo purposes, we will use a static list here
    target_list = [
        "www.mozilla.org",
        "infosec.mozilla.org",
    ]
    randomizer = Randomizer(target_list)
    target = Target(randomizer.next())
    if target.isValid():
        logger.info("Tasking observatory scan of: " +
                    target.targetname)
        scanner = HTTPObservatoryScanner()
        scan_result = scanner.scan(target.targetname)
        logger.info("Completed observatory scan of " +
                    target.targetname)
        send_to_s3(target.targetname + "_observatory", scan_result)
    else:
        logger.error("Target validation failed of: " +
                     target.targetname)


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
    if target.isValid():
        print(SQS_CLIENT.send_message(
              QueueUrl=os.getenv('SQS_URL'),
              MessageBody="manual|" + target.targetname
              ))
