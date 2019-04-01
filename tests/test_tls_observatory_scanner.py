
import pytest
import os
import requests
from scanners.tls_observatory_scanner import TLSObservatoryScanner


class TestTLSObservatoryScanner():
    def test_defaults(self):
        scanner = TLSObservatoryScanner()
        assert scanner.poll_interval == 1
        # This is expected to be None because the API value lives
        # in Serverless Lambda environment, not locally
        assert scanner.api_url == None

    def test_setting_poll_interval(self):
        scanner = TLSObservatoryScanner(2)
        assert scanner.poll_interval == 2
        # Same as above function
        assert scanner.api_url == None

    def test_setting_api_url(self):
        # Stub env var for testing
        os.environ["TLSOBS_API_URL"] = "https://tls-observatory.services.mozilla.com/api/v1"

        scanner = TLSObservatoryScanner()
        assert scanner.poll_interval == 1
        assert scanner.api_url == os.environ["TLSOBS_API_URL"]

        # Unstub env var for testing
        os.environ["TLSOBS_API_URL"] = ""

    def test_scan(self):
        # Stub env var for testing
        os.environ["TLSOBS_API_URL"] = "https://tls-observatory.services.mozilla.com/api/v1"
        host_name = "www.mozilla.org"
        scanner = TLSObservatoryScanner()
        scan_result = scanner.scan(host_name)

        # Check to see is some of the expected JSON elements
        # are in the scan result to ensure it's working
        assert 'host' in scan_result
        assert 'scan' in scan_result
        assert 'completion_perc' in scan_result['scan']

        # Unstub env var for testing
        os.environ["TLSOBS_API_URL"] = ""
