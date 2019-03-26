
import pytest
import boto3
from lib.tlsobsscan_handler import TLSObsScanHandler
from moto import mock_sqs
from uuid import UUID


class TestTLSObsScanHandler():
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

    def test_creation(self):
        tlsobs_scan_handler = TLSObsScanHandler()
        assert type(tlsobs_scan_handler) is TLSObsScanHandler

    def test_queue(self, sqs):
        client, queue_url = sqs
        test_event = {"body": '{"target": "ssh.mozilla.com"}'}
        test_context = None
        tlsobs_scan_handler = TLSObsScanHandler(client, queue_url)
        tlsobs_scan_handler.queue(test_event, test_context)
        response = client.receive_message(QueueUrl=queue_url)
        scan_type, target, uuid = response['Messages'][0]['Body'].split('|')
        assert scan_type == "tlsobservatory"
        assert target == "ssh.mozilla.com"
        assert UUID(uuid, version=4)

