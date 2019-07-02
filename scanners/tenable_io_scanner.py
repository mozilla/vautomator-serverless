import requests
import time
import os
import logging
import json
import boto3
from lib.custom_exceptions import TenableScanRunningException, TenableScanUnexpectedStateException, TenableScanInterruptedException
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException, TenableIOException
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
        self.client = self.__createClient()
        if (self.client):
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
        else:
            return False

    def scanResult(self, scan_id):
        if self.__poll(scan_id):
            nscan = self.client.scan_helper.id(scan_id)
            # Scan Details Object to dict
            scan_details = nscan.details().as_payload()
            # This is a work-around, taken from: https://github.com/tenable/Tenable.io-SDK-for-Python/issues/84
            # Hosts Objects to dicts
            scan_details['hosts'] = [host.as_payload() for host in scan_details['_hosts']]
            del scan_details['_hosts']
            # History Objects to dicts
            scan_details['history'] = [host.as_payload() for host in scan_details['_history']]
            del scan_details['_history']
            # Info Object to dict
            scan_details['info'] = vars(scan_details['_info'])
            del scan_details['_info']

            return scan_details
        else:
            raise TenableScanUnexpectedStateException("Tenable.io scan in unexpected state.")

    def __poll(self, scan_id):
        # This function will poll Tenable.io API for a scan status
        # Query Tenable API to check if the scan is finished
        self.client = self.__createClient()
        scan_ref = self.client.scan_helper.id(scan_id)
        status = scan_ref.status()

        if status == Scan.STATUS_COMPLETED:
            return True
        elif status == Scan.STATUS_ABORTED or status == Scan.STATUS_CANCELED or status == Scan.STATUS_STOPPING:
            raise TenableScanInterruptedException("Tenable.io scan ended abruptly, likely stopped or aborted manually.")
        elif status == Scan.STATUS_INITIALIZING or status == Scan.STATUS_PENDING or status == Scan.STATUS_RUNNING:
            raise TenableScanRunningException("Tenable.io scan still underway.")
        else:
            self.logger.error("Something is wrong with Tenable.io scan. Check the TIO console manually.")
            return False

    def __getAPIKey(self):
        response = self.ssm_client.get_parameter(Name="TENABLEIO_ACCESS_KEY", WithDecryption=True)
        access_key = response['Parameter']['Value']
        response = self.ssm_client.get_parameter(Name="TENABLEIO_SECRET_KEY", WithDecryption=True)
        secret_key = response['Parameter']['Value']
        return access_key, secret_key

    def __createClient(self):
        # If not passed at the time of object instantiation
        if not self.tio_access_key or not self.tio_secret_key:
            try:
                # See if we can load the API keys from SSM
                self.tio_access_key, self.tio_secret_key = self.__getAPIKey()
            except Exception:
                self.logger.error("Cannot obtain Tenable.io API key(s), skipping Tenable.io scan")
                return False

        # Here, we have the keys, either from SSM or from instantiation
        client = TenableIOClient(access_key=self.tio_access_key, secret_key=self.tio_secret_key)
        return client
