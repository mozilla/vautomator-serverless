import requests
import time
import os
import logging
import json
import boto3
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
from tenable_io.api.scans import ScanExportRequest
from tenable_io.api.models import Scan


class TIOScanner():
    def __init__(
        self, access_key=None, secret_key=None,
        ssm_client=boto3.client('ssm', region_name='us-west-2'),
        report_format="html",
        logger=logging.getLogger(__name__)
    ):
        self.ssm_client = ssm_client
        self.client = None
        self.tio_access_key = access_key
        self.tio_secret_key = secret_key
        self.report_format = report_format
        self.logger = logger

    def scan(self, hostname):
        # If not passed at the time of object instantiation
        if not self.tio_access_key or not self.tio_secret_key:
            try:
                # See if we can load the API keys from SSM
                self.tio_access_key, self.tio_secret_key = self.__getAPIKey()
            except Exception:
                self.logger.error("Cannot obtain Tenable.io API key(s), skipping Tenable.io scan")
                return False

        # Here, we have the keys, either from SSM or from instantiation
        self.client = TenableIOClient(access_key=self.tio_access_key, secret_key=self.tio_secret_key)
        # Reference: https://github.com/tenable/Tenable.io-SDK-for-Python/blob/master/examples/scans.py
        try:
            # Run a basic network scan on the target
            scan_name = "VA for " + hostname
            nscan = self.client.scan_helper.create(
                name=scan_name, text_targets=hostname, template='basic'
            )
            return nscan

        except Exception as TIOException:
            self.logger.error("Tenable.io scan failed: {}".format(TIOException))
            return False

    def scanResult(self, scan_ref):
        nscan = self.client.scan_helper.id(scan_ref.id)
        # Scan Details Object to dict
        scan_details = nscan.details().as_payload()
        return json.dumps(scan_details)

    def __getAPIKey(self):
        response = self.ssm_client.get_parameter(Name="TENABLEIO_ACCESS_KEY", WithDecryption=True)
        access_key = response['Parameter']['Value']
        response = self.ssm_client.get_parameter(Name="TENABLEIO_SECRET_KEY", WithDecryption=True)
        secret_key = response['Parameter']['Value']
        return access_key, secret_key
