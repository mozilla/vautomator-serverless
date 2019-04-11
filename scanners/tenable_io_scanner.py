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
        # First, check to see if we can read the API keys
        if self.tio_access_key == "" or self.tio_secret_key == "":
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

    def __downloadReport(self, nscan, reportformat="html", style="assets"):
        report_path = ("/app/results/" + (self.tasktarget).targetdomain
                       + "/Scan_for_" + (self.tasktarget).targetdomain
                       + "." + reportformat)

        if reportformat == "html":
            fmt = ScanExportRequest.FORMAT_HTML
        elif reportformat == "pdf":
            fmt = ScanExportRequest.FORMAT_PDF
        elif reportformat == "csv":
            fmt = ScanExportRequest.FORMAT_CSV
        elif reportformat == "nessus":
            fmt = ScanExportRequest.FORMAT_NESSUS
        elif reportformat == "db":
            fmt = ScanExportRequest.FORMAT_DB
        else:
            return False

        if style == "assets":
            reportoutline = ScanExportRequest.CHAPTER_CUSTOM_VULN_BY_HOST
        elif style == "exec":
            reportoutline = ScanExportRequest.CHAPTER_EXECUTIVE_SUMMARY
        elif style == "plugins":
            reportoutline = ScanExportRequest.CHAPTER_CUSTOM_VULN_BY_PLUGIN
        else:
            return False

        nscan.download(report_path, format=fmt, chapter=reportoutline)

    def __checkScanStatus(self, nscan):
        # Query Tenable API to check if the scan is finished
        status = nscan.status()

        if status == Scan.STATUS_COMPLETED:
            return "COMPLETE"
        elif status == Scan.STATUS_ABORTED:
            return "ABORTED"
        elif status == Scan.STATUS_INITIALIZING:
            return "INITIALIZING"
        elif status == Scan.STATUS_PENDING:
            return "PENDING"
        elif status == Scan.STATUS_RUNNING:
            return "RUNNING"
        else:
            self.logger.error("[-] Something is wrong with Tenable.io scan. Check the TIO console manually.")
            return False

    def __getAPIKey(self, key_type):

        return
