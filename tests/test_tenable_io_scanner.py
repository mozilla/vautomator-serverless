import sys
import pytest
import os
import json
import requests
from scanners.tenable_io_scanner import TIOScanner
from lib.target import Target
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
from tenable_io.api.scans import ScanExportRequest
from tenable_io.api.models import Scan


class TestTIOScanner():
    def test_defaults(self):
        scanner = TIOScanner()
        assert scanner.client is None
        assert scanner.tio_access_key is None
        assert scanner.tio_secret_key is None
        assert scanner.report_format == "html"

    def test_scan(self):
        