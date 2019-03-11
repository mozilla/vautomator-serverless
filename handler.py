import json
import logging
import boto3
import os

from util.s3_helper import send_to_s3
from lib.target import Target
from scanners.httpobs_scanner import HTTPObservatoryScanner
from scanners.port_scanner import PortScanner
from util.host_picker import Randomizer
from util.response import Response
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from util.randomizer import Randomizer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runUDP(event, context):
    data = json.loads(event['body'])
    target = Target(data.get('target'))

    if not target.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'target was not valid or missing'})
         }).with_security_headers()
    
    port_scanner = PortScanner()
    udp_results = port_scanner.scanUDP(target.targetname)
    logger.info(udp_results)
    if udp_results:
        return Response({
            "statusCode": 200,
            "body": json.dumps({'OK': 'target added to the queue'})
        }).with_security_headers()
    else:
        return Response({
            "statusCode": 500,
            "body": json.dumps({'error': 'MEH'})
        }).with_security_headers()


def runTCP(event, context):
    data = json.loads(event['body'])
    target = Target(data.get('target'))

    if not target.isValid():
        logger.error("Target Validation Failed of: " +
                     json.dumps(target.targetname))
        return Response({
             "statusCode": 400,
             "body": json.dumps({'error': 'target was not valid or missing'})
         }).with_security_headers()
    
    port_scanner = PortScanner()
    tcp_results = port_scanner.scanTCP(target.targetname)
    logger.info(tcp_results)

    if tcp_results:
        return Response({
            "statusCode": 200,
            "body": json.dumps({'OK': 'target added to the queue'})
        }).with_security_headers()


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
        logger.info("Tasking Observatory Scan of: " +
                    json.dumps(target.targetname))
        scan_result = scanner.scan(target)
        logger.info("Completed Observatory Scan of " +
                    json.dumps(target.targetname))
        send_to_s3(target.targetname, scan_result)
