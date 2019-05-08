import pytest
import boto3
import time
from lib.direnum_scan_handler import DirectoryEnumScanHandler
from lib.hosts import Hosts
from moto import mock_sqs
from uuid import UUID


class TestDirectoryEnumScanHandler():
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
        direnum_scan_handler = DirectoryEnumScanHandler()
        assert type(direnum_scan_handler) is DirectoryEnumScanHandler

    def test_queue(self, sqs):
        client, queue_url = sqs
        test_event = {"body": '{"target": "infosec.mozilla.org"}'}
        test_context = None
        direnum_scan_handler = DirectoryEnumScanHandler(client, queue_url)
        direnum_scan_handler.queue(test_event, test_context)
        response = client.receive_message(QueueUrl=queue_url)
        scan_type, target, uuid = response['Messages'][0]['Body'].split('|')
        assert scan_type == "direnumscan"
        assert target == "infosec.mozilla.org"
        assert UUID(uuid, version=4)

    def test_queue_scheduled(self, sqs):
        client, queue_url = sqs
        test_hostlist = [
            "ssh.mozilla.com",
            "infosec.mozilla.org",
            "mozilla.org"
        ]
        index = 0
        test_event = None
        test_context = None
        direnum_scan_handler = DirectoryEnumScanHandler(client, queue_url)
        direnum_scan_handler.queue_scheduled(test_event, test_context, test_hostlist)

        # Need to sleep here for at least 6 seconds as queue messages
        # have 2 seconds delay until become available
        time.sleep(7)
        response = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=3)
        for msg in response['Messages']:
            scan_type, target, placeholder = msg['Body'].split('|')
            assert scan_type == "direnumscan"
            assert target == test_hostlist[index]
            assert placeholder == ""
            index += 1
