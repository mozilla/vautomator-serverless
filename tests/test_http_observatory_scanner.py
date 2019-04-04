import sys
import pytest
import os
import json
import requests
from scanners.http_observatory_scanner import HTTPObservatoryScanner
from lib.target import Target


class TestHTTPObservatoryScanner():
    def test_defaults(self):
        scanner = HTTPObservatoryScanner()
        assert scanner.poll_interval == 1
        assert scanner.api_url is None

    def test_setting_poll_interval(self):
        scanner = HTTPObservatoryScanner(2)
        assert scanner.poll_interval == 2
        assert scanner.api_url is None

    def test_setting_api_url(self):
        # Stub env var for testing
        os.environ["HTTPOBS_API_URL"] = "https://http-observatory.security.mozilla.org/api/v1"

        scanner = HTTPObservatoryScanner()
        assert scanner.poll_interval == 1
        assert scanner.api_url == os.environ["HTTPOBS_API_URL"]

        # Unstub env var for testing
        os.environ["HTTPOBS_API_URL"] = ""

    def test_scan(self):
        # Stub env var for testing
        os.environ["HTTPOBS_API_URL"] = "https://http-observatory.security.mozilla.org/api/v1"
        host_name = "www.mozilla.org"
        scanner = HTTPObservatoryScanner()
        scan_result = scanner.scan(host_name)

        # Check to see is some of the expected JSON elements
        # are in the scan result to ensure it's working
        assert 'host' in scan_result
        assert 'scan' in scan_result
        assert 'grade' in scan_result['scan']

        # Unstub env var for testing
        os.environ["HTTPOBS_API_URL"] = ""
