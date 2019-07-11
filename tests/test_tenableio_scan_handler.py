import pytest
import boto3
import time
import os
import responses
from lib.tenableio_scan_handler import TIOScanHandler
from scanners.tenable_io_scanner import TIOScanner
from lib.hosts import Hosts
from moto import mock_sqs, mock_s3
from uuid import UUID


class TestTIOScanHandler():
    @pytest.fixture
    def sqs(self, scope="session", autouse=True):
        mock = mock_sqs()
        mock.start()
        # There is currently a bug on moto, this line is needed as a workaround
        # Ref: https://github.com/spulec/moto/issues/1926
        boto3.setup_default_session()

        sqs_client = boto3.client('sqs', 'us-west-2')
        queue_name = "test-scan-queue"
        queue_url = sqs_client.create_queue(
            QueueName=queue_name
        )['QueueUrl']

        yield (sqs_client, queue_url)
        mock.stop()

    @pytest.fixture
    def s3(self, scope="session", autouse=True):
        mock = mock_s3()
        mock.start()
        responses.add_passthru('https://')
        # There is currently a bug on moto, this line is needed as a workaround
        # Ref: https://github.com/spulec/moto/issues/1926
        boto3.setup_default_session()

        s3_client = boto3.client('s3', 'us-west-2')
        test_bucket_name = "test-results-handler"
        test_bucket = s3_client.create_bucket(
            Bucket=test_bucket_name,
            ACL='public-read'
        )

        yield (s3_client, test_bucket, test_bucket_name)
        mock.stop()

    def test_creation(self):
        tenableio_scan_handler = TIOScanHandler()
        assert type(tenableio_scan_handler) is TIOScanHandler

    def test_queue(self, sqs):
        client, queue_url = sqs
        test_event = {"body": '{"target": "infosec.mozilla.org"}'}
        test_context = None
        tenableio_scan_handler = TIOScanHandler(client, queue_url)
        tenableio_scan_handler.queue(test_event, test_context)
        response = client.receive_message(QueueUrl=queue_url)
        scan_type, target, uuid = response['Messages'][0]['Body'].split('|')
        assert scan_type == "tenableio"
        assert target == "infosec.mozilla.org"
        assert UUID(uuid, version=4)

    # This will work in Travis, because we use secure
    # env variables to store API keys. Let's not risk
    # leaking them locally, so do not run this if
    # running locally (i.e. only run in Travis)
    @pytest.mark.skipif("TRAVIS" not in os.environ
                        and not os.getenv("TRAVIS"),
                        reason="Only run this test on Travis CI.")
    def test_runFromStepFunction(self):
        target = "infosec.mozilla.org"
        partial_stepf_event = {"target": target}
        test_context = None
        try:
            a_key = os.environ["TIOA"]
            s_key = os.environ["TIOS"]
        except Exception:
            assert False
        tenableio_scan_handler = TIOScanHandler()
        response = tenableio_scan_handler.runFromStepFunction(partial_stepf_event, test_context)
        assert type(response) is dict

        # The next few lines are for cleaning up,
        # we should abort the scan just launched
        scan_id = response['id']
        scanner = TIOScanner(access_key=a_key, secret_key=s_key)
        client = scanner._TIOScanner__createClient()
        scan_ref = client.scan_helper.id(scan_id)
        scan_ref.stop(wait=False)

        test_invalid_event = {"TEST": "TEST"}
        invalid_response = tenableio_scan_handler.runFromStepFunction(test_invalid_event, test_context)
        assert invalid_response is False

    # This will work in Travis, because we use secure
    # env variables to store API keys. Let's not risk
    # leaking them locally, so do not run this if
    # running locally (i.e. only run in Travis)
    @pytest.mark.skipif("TRAVIS" not in os.environ
                        and not os.getenv("TRAVIS"),
                        reason="Only run this test on Travis CI.")
    def test_pollScanResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        partial_stepf_event = {
            "target": target,
            "responses": {
                "Tenablescan": {
                    "id": 453
                }
            }
        }
        test_context = None
        tenableio_scan_handler = TIOScanHandler(s3_client=client, bucket=bucket_name)
        resp = tenableio_scan_handler.pollScanResults(partial_stepf_event, test_context)
        assert type(resp) is dict
        assert resp['statusCode'] == 200
