import logging
import boto3
import os
from lib.s3_helper import send_to_s3
from lib.target import Target
from lib.hosts import Hosts
from lib.portscan_handler import PortScanHandler
from lib.httpobsscan_handler import HTTPObsScanHandler
from lib.tlsobsscan_handler import TLSObsScanHandler
from lib.sshscan_handler import SSHScanHandler
from lib.tenableio_scan_handler import TIOScanHandler
from lib.websearch_handler import WebSearchHandler
from lib.direnum_scan_handler import DirectoryEnumScanHandler
from lib.results_handler import ResultsHandler
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from scanners.ssh_observatory_scanner import SSHObservatoryScanner
from scanners.tls_observatory_scanner import TLSObservatoryScanner
from scanners.port_scanner import PortScanner
from scanners.tenable_io_scanner import TIOScanner
from scanners.websearcher import WebSearcher
from scanners.direnum_scanner import DirectoryEnumScanner

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SQS_CLIENT = boto3.client('sqs')
S3_CLIENT = boto3.client('s3')
S3_BUCKET = os.environ.get('S3_BUCKET')


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


def queue_tenableioscan(event, context):
    tenableio_scan_handler = TIOScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = tenableio_scan_handler.queue(event, context)
    return response


def check_tenableioscan(event, context):
    tenableio_scan_handler = TIOScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = tenableio_scan_handler.pollScanResults(event, context)
    return response


def queue_websearch(event, context):
    websearch_handler = WebSearchHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = websearch_handler.queue(event, context)
    return response


def queue_direnumscan(event, context):
    direnum_scan_handler = DirectoryEnumScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    response = direnum_scan_handler.queue(event, context)
    return response


def queue_scheduled_direnumscan(event, context):
    scheduled_direnum_scan_handler = DirectoryEnumScanHandler(sqs_client=SQS_CLIENT, logger=logger)
    scheduled_direnum_scan_handler.queue_scheduled(event, context)


def download_results(event, context):
    results_handler = ResultsHandler(s3_client=S3_CLIENT, logger=logger)
    response = results_handler.getResults(event, context)
    return response


# To leave handler as lean as possible, we should
# probably move this to another file/module also
def runScanFromQ(event, context):

    # This is needed for nmap static library and
    # dirb to be added to the path
    _environ = dict(os.environ)
    nmap_path = os.environ['LAMBDA_TASK_ROOT'] + '/vendor/nmap-standalone/'
    dirb_path = os.environ['LAMBDA_TASK_ROOT'] + '/vendor/dirb/'
    try:
        os.environ.update({'PATH': os.environ['PATH'] + ':' + nmap_path + ':' + dirb_path})
        # Read the queue
        for record, keys in event.items():
            for item in keys:
                if "body" in item:
                    message = item['body']
                    scan_type, target, uuid = message.split('|')
                    if scan_type == "httpobservatory":
                        scanner = HTTPObservatoryScanner()
                        scan_result = scanner.scan(target)
                        send_to_s3(target + "_httpobservatory", scan_result, client=S3_CLIENT, bucket=S3_BUCKET)
                    elif scan_type == "sshobservatory":
                        scanner = SSHObservatoryScanner()
                        scan_result = scanner.scan(target)
                        send_to_s3(target + "_sshobservatory", scan_result, client=S3_CLIENT, bucket=S3_BUCKET)
                    elif scan_type == "tlsobservatory":
                        scanner = TLSObservatoryScanner()
                        scan_result = scanner.scan(target)
                        send_to_s3(target + "_tlsobservatory", scan_result, client=S3_CLIENT, bucket=S3_BUCKET)
                    elif scan_type == "portscan":
                        scanner = PortScanner(target)
                        nmap_scanner = scanner.scanTCP()
                        while nmap_scanner.still_scanning():
                            # Wait for 1 second after the end of the scan
                            nmap_scanner.wait(1)
                    elif scan_type == "tenableio":
                        scanner = TIOScanner(logger=logger)
                        nessus_scanner = scanner.scan(target)
                        nessus_scanner.launch(wait=False)
                    elif scan_type == "websearch":
                        searcher = WebSearcher(logger=logger)
                        search_results = searcher.search(target)
                        send_to_s3(target + "_websearch", search_results, client=S3_CLIENT, bucket=S3_BUCKET)
                    elif scan_type == "direnumscan":
                        scanner = DirectoryEnumScanner(logger=logger)
                        return_code, direnum_result = scanner.scan(target)
                        send_to_s3(target + "_direnum", direnum_result, client=S3_CLIENT, bucket=S3_BUCKET)
                    else:
                        # Manually invoked, just log the message
                        logger.info("Message in queue: {}".format(message))
                else:
                    logger.error("Unrecognized message in queue: {}".format(message))

    except Exception as e:
        logger.error("Exception occurred while running scans from the queue: {}".format(e))
    finally:
        # Restore environment variables to their original values
        os.environ.update(_environ)


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
