import logging
import boto3
import os

from lib.s3_helper import send_to_s3
from lib.target import Target
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from scanners.ssh_observatory_scanner import SSHObservatoryScanner
from scanners.tls_observatory_scanner import TLSObservatoryScanner
from scanners.port_scanner import PortScanner
from lib.hosts import Hosts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def runScanFromQ(event, context):

    # This is needed for nmap static library to be added to the path
    original_pathvar = os.environ['PATH']
    os.environ['PATH'] = original_pathvar \
        + ':' + os.environ['LAMBDA_TASK_ROOT'] \
        + '/vendor/nmap-standalone/'

    # Read the queue
    for record, keys in event.items():
        for item in keys:
            if "body" in item:
                message = item['body']
                scan_type, target, uuid = message.split('|')
                if scan_type == "httpobservatory":
                    scanner = HTTPObservatoryScanner()
                    scan_result = scanner.scan(target)
                    send_to_s3(target + "_httpobservatory", scan_result)
                elif scan_type == "sshobservatory":
                    scanner = SSHObservatoryScanner()
                    scan_result = scanner.scan(target)
                    send_to_s3(target + "_sshobservatory", scan_result)
                elif scan_type == "tlsobservatory":
                    scanner = TLSObservatoryScanner()
                    scan_result = scanner.scan(target)
                    send_to_s3(target + "_tlsobservatory", scan_result)
                elif scan_type == "portscan":
                    scanner = PortScanner(target)
                    nmap_scanner = scanner.scanTCP()
                    while nmap_scanner.still_scanning():
                        # Wait for 1 second after the end of the scan
                        nmap_scanner.wait(1)
                else:
                    # Manually invoked, just log the message
                    logger.info("Message in queue: " +
                                message)
            else:
                logger.error("Unrecognized message in queue: " +
                             message)

    os.environ['PATH'] = original_pathvar


def putInQueue(event, context):
    # For demo purposes, this function is invoked manually
    # Also for demo purposes, we will use a static list here
    # We need to figure out a way to put stuff in the queue regularly
    target_list = [
        "www.mozilla.org",
        "infosec.mozilla.org",
    ]
    hosts = Hosts(target_list)
    target = Target(hosts.next())
    SQS_CLIENT.send_message(
        QueueUrl=os.getenv('SQS_URL'),
        MessageBody="manual|" + target.name
    )
