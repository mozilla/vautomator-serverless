import sys
import pytest
import os
import json
import requests
from scanners.ssh_observatory_scanner import SSHObservatoryScanner
from lib.target import Target


class TestSSHObservatoryScanner():
    def test_defaults(self):
        scanner = SSHObservatoryScanner()
        assert scanner.poll_interval == 1
        assert scanner.api_url == None

    def test_setting_poll_interval(self):
        scanner = SSHObservatoryScanner(2)
        assert scanner.poll_interval == 2
        assert scanner.api_url == None

    def test_setting_api_url(self):
        # Stub env var for testing
        os.environ["SSHOBS_API_URL"] = "https://sshscan.rubidus.com/api/v1"

        scanner = SSHObservatoryScanner()
        assert scanner.poll_interval == 1
        assert scanner.api_url == os.environ["SSHOBS_API_URL"]

        # Unstub env var for testing
        os.environ["SSHOBS_API_URL"] = ""

    def test_scan(self):
        # Stub env var for testing
        os.environ["SSHOBS_API_URL"] = "https://sshscan.rubidus.com/api/v1"
        host_name = "ssh.mozilla.com"
        scanner = SSHObservatoryScanner()
        scan_result = scanner.scan(host_name)

        # Check to see is some of the expected JSON elements
        # are in the scan result to ensure it's working
        assert 'ssh_scan_version' in scan_result['scan']
        assert 'ip' in scan_result['scan']
        assert 'hostname' in scan_result['scan']

        # Unstub env var for testing
        os.environ["SSHOBS_API_URL"] = ""
