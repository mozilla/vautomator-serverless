import nmap
import boto3
import os
import logging
from lib.s3_helper import send_to_s3
from lib.utilities import sanitise_shell_cmd

S3_BUCKET = os.getenv('S3_BUCKET')
REGION = os.getenv('REGION', 'us-west-2')
S3_CLIENT = boto3.client('s3', region_name=REGION)


class PortScanner():

    def __init__(self, hostname, arguments="-v -Pn -sT -sV --script=banner --top-ports 1000 --open -T4 --system-dns", logger=logging.getLogger(__name__)):
        self.host = hostname
        self.arguments = "".join(sanitise_shell_cmd(arguments))
        self.privileged = False
        self.logger = logger

    def scanTCP(self, callback_function=None):
        self.logger.info("Running TCP port  scan on {}...".format(self.host))
        nma = nmap.PortScannerAsync()
        if not callback_function:
            nma.scan(self.host, arguments=self.arguments,
                     sudo=self.privileged,
                     callback=self.callback_results
                     )
        else:
            nma.scan(self.host, arguments=self.arguments,
                     sudo=self.privileged,
                     callback=callback_function
                     )
        return nma

    def callback_results(self, hostname, scan_result):
        send_to_s3(self.host + "_tcpscan", scan_result, client=S3_CLIENT, bucket=S3_BUCKET)
