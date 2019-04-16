import sys
import pytest
import os
import json
import requests
import boto3
from scanners.tenable_io_scanner import TIOScanner
from lib.target import Target
from moto import mock_ssm
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException, TenableIOErrorCode
from tenable_io.api.scans import ScanExportRequest
from tenable_io.api.models import Scan


class TestTIOScanner():
    # Approach taken here is to create a dedicated Tenable.io
    # account just for test purposes, and use Travis CI's
    # "secure" method to store the credentials, use those
    # credentials to test the "scan" method.

    # Mocking SSM here so we can tes the __getAPIKey() method
    @pytest.fixture
    def ssm(self, scope="session", autouse=True):
        mock = mock_ssm()
        mock.start()
        # There is currently a bug on moto, this line is needed as a workaround
        # Ref: https://github.com/spulec/moto/issues/1926
        boto3.setup_default_session()

        ssm_client = boto3.client('ssm', 'us-west-2')
        ssm_client.put_parameter(
            Name="TENABLEIO_ACCESS_KEY",
            Description="Bogus access key.",
            Value="TEST",
            Type="SecureString"
        )

        ssm_client.put_parameter(
            Name="TENABLEIO_SECRET_KEY",
            Description="Bogus secret key.",
            Value="TEST",
            Type="SecureString"
        )

        yield ssm_client
        mock.stop()

    def test_defaults(self, ssm):
        scanner = TIOScanner(ssm_client=ssm)
        assert scanner.client is None
        assert scanner.tio_access_key is None
        assert scanner.tio_secret_key is None
        assert scanner.report_format == "html"
        assert scanner.ssm_client == ssm

    def test_tenable_auth_fail(self):
        try:
            TenableIOClient('test', 'test').session_api.get()
            assert False
        except TenableIOApiException as e:
            assert e.code is TenableIOErrorCode.UNAUTHORIZED

    def test_tenable_auth_success(self):
        # See if the keys are available as env variables
        try:
            a_key = os.environ["TIOA"]
            s_key = os.environ["TIOS"]
        except Exception:
            assert False
        # See if we can use those keys to successfully
        # authenticate to Tenable.io, should be True
        try:
            TenableIOClient(a_key, s_key).session_api.get()
            assert True
        except TenableIOApiException as e:
            assert e.code is TenableIOErrorCode.UNAUTHORIZED

    def test__getAPIKey(self, ssm):
        scanner = TIOScanner(ssm_client=ssm)
        test_akey, test_skey = scanner._TIOScanner__getAPIKey()
        assert test_akey == "TEST"
        assert test_skey == "TEST"

    def test_scan(self):
        # See if the keys are available as env variables
        try:
            a_key = os.environ["TIOA"]
            s_key = os.environ["TIOS"]
        except Exception:
            assert False
        host_name = "www.mozilla.org"
        scanner = TIOScanner(access_key=a_key, secret_key=s_key)
        nscan = scanner.scan(host_name)

        # Ref: https://github.com/tenable/Tenable.io-SDK-for-Python/blob/master/tests/integration/helpers/test_scan.py
        # nscan is a ScanRef object.
        # Note that we are NOT launching the scan here, we do not
        # want an actual scan to be kicked off as a part of CI
        # scan_details is a scan_detail object
        scan_detail = nscan.details()
        # ScanRef object ID should the ScanDetail object ID
        assert scan_detail.info.object_id == nscan.id
        nscan.delete(force_stop=True)
