import requests
import time
import os
import logging
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
from tenable_io.api.scans import ScanExportRequest
from tenable_io.api.models import Scan


class TIOScanner():
    def __init__(self, report_format="html", logger=logging.getLogger(__name__)):
        # We should probably change this, read from SSM or something similar
        self.client = None
        self.tio_access_key = None
        self.tio_secret_key = None
        self.report_format = report_format
        self.logger = logger
    
    def scan(self, hostname):
        # First, 
        try:
            # Check to see if we can load the API keys
            self.tio_access_key, self.tio_secret_key = self.__getAPIKey()
        except Exception:
            raise Exception(
                "[!] Cannot obtain Tenable.io API key(s), skipping Tenable.io scan."
            )
            return False

        # We can obtain the keys
        self.client = TenableIOClient(access_key=self.tio_access_key, secret_key=self.tio_secret_key)
        # Reference: https://github.com/tenable/Tenable.io-SDK-for-Python/blob/master/examples/scans.py
        try:
            # Run a basic network scan on the target
            scan_name = "VA for " + hostname
            new_nscan = self.client.scan_helper.create(
                name=scan_name, text_targets=self.tasktarget.targetdomain, template="basic"
            )
            new_nscan.launch(wait=False)

        except TenableIOApiException as TIOException:
            self.logger.error("[-] Tenable.io scan failed: {}".format(TIOException))

    def __getAPIKey(self):

        return a_key, s_key
