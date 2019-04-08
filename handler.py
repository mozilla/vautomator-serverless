import logging
import boto3
import os
from lib.s3_helper import send_to_s3
from lib.target import Target
from lib.portscan_handler import PortScanHandler
from lib.httpobsscan_handler import HTTPObsScanHandler
from lib.tlsobsscan_handler import TLSObsScanHandler
from lib.sshscan_handler import SSHScanHandler
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from scanners.ssh_observatory_scanner import SSHObservatoryScanner
from scanners.tls_observatory_scanner import TLSObservatoryScanner
from scanners.port_scanner import PortScanner
from lib.hosts import Hosts


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')


def queue_portscan(event, context):
    port_scan_handler = PortScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = port_scan_handler.queue(event, context)
    return response


def queue_scheduled_portscan(event, context):
    scheduled_portscan_handler = PortScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    scheduled_portscan_handler.queue_scheduled(event, context)


def queue_httpboservatory(event, context):
    httpobservatory_handler = HTTPObsScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = httpobservatory_handler.queue(event, context)
    return response


def queue_scheduled_httpobservatory(event, context):
    scheduled_httpobservatory_handler = HTTPObsScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    scheduled_httpobservatory_handler.queue_scheduled(event, context)


def queue_tlsobservatory(event, context):
    tlsobservatory_handler = TLSObsScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = tlsobservatory_handler.queue(event, context)
    return response


def queue_scheduled_tlsobservatory(event, context):
    scheduled_tlsobservatory_handler = TLSObsScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    scheduled_tlsobservatory_handler.queue_scheduled(event, context)


def queue_sshobservatory(event, context):
    sshobservatory_handler = SSHScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = sshobservatory_handler.queue(event, context)
    return response


def queue_scheduled_sshobservatory(event, context):
    scheduled_sshobservatory_handler = SSHScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    scheduled_sshobservatory_handler.queue_scheduled(event, context)


# To leave handler as lean as possible, we should
# probably move this to another file/module also
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
                    logger.info("Message in queue: {}".format(message))
            else:
                logger.error("Unrecognized message in queue: {}".format(message))

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
