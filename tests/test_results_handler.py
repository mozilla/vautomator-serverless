import pytest
import os
import boto3
import json
from moto import mock_s3
from lib.results_handler import ResultsHandler
from lib.s3_helper import create_presigned_url
from urllib.parse import urlparse, parse_qs

TEST_SCAN_RESULTS_BASE_PATH = '/tmp/vautomator-serverless/results'


class TestResultsHandler():

    @pytest.fixture
    def s3(self, scope="session", autouse=True):
        mock = mock_s3()
        mock.start()
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
        results_handler = ResultsHandler()
        assert type(results_handler) is ResultsHandler

    def test_downloadResults_fullResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # Ensure we have all matching objects in the test S3 bucket
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_direnum.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_websearch.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tcpscan.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_httpobservatory.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tlsobservatory.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_sshobservatory.json'.format(target))

        test_apigw_event = {"body": '{"target": "' + target + '"}'}
        test_context = None
        results_handler = ResultsHandler(s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.downloadResults(test_apigw_event, test_context)
        assert response['statusCode'] == 200
        assert response['isBase64Encoded'] is True
        assert 'Content-Disposition' in response['headers']
        assert response['headers']['Content-Type'] == "application/gzip"

    def test_downloadResults_partialResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # We only have some (partial) results in the S3 bucket
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_direnum.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_websearch.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tcpscan.json'.format(target))

        test_apigw_event = {"body": '{"target": "' + target + '"}'}
        test_context = None
        results_handler = ResultsHandler(s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.downloadResults(test_apigw_event, test_context)
        assert response['statusCode'] == 202
        assert response['isBase64Encoded'] is True
        assert 'Content-Disposition' in response['headers']
        assert response['headers']['Content-Type'] == "application/gzip"

    def test_downloadResults_noResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # No objects in the S3 bucket, should return no results
        test_apigw_event = {"body": '{"target": "' + target + '"}'}
        test_context = None
        results_handler = ResultsHandler(client, bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.downloadResults(test_apigw_event, test_context)

        assert type(response) is dict
        assert response['statusCode'] == 404
        assert 'isBase64Encoded' not in response
        assert 'Content-Disposition' not in response['headers']
        assert response['headers']['Content-Type'] == "application/json"
        assert 'no' in response['body'].lower()

    def test_downloadResults_unableToDownload(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        path = "/abc/def"  # A path that does not exist

        # Ensure we have matching objects in the test S3 bucket to rule out other failure scenario
        client.put_object(Bucket=bucket_name, Body=b'ABCD', Key='{}_direnum.json'.format(target))
        client.put_object(Bucket=bucket_name, Body=b'ABCD', Key='{}_websearch.json'.format(target))
        test_apigw_event = {"body": '{"target": "' + target + '"}'}
        test_context = None
        results_handler = ResultsHandler(client, bucket_name, results_path=path)
        response = results_handler.downloadResults(test_apigw_event, test_context)

        assert type(response) is dict
        assert response['statusCode'] == 500
        assert 'isBase64Encoded' not in response
        assert 'Content-Disposition' not in response['headers']
        assert response['headers']['Content-Type'] == "application/json"
        assert 'unable' in response['body'].lower()

    def test_downloadResults_invalidEvent(self, s3):
        client, bucket, bucket_name = s3
        invalid_event = {"TEST": "TEST"}
        test_context = None
        results_handler = ResultsHandler(client, bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.downloadResults(invalid_event, test_context)

        assert type(response) is dict
        assert response['statusCode'] == 400
        assert 'unrecognized' in response['body'].lower()

    def test_generateDownloadLink_fullResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # Ensure we have all matching objects in the test S3 bucket
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_direnum.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_websearch.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tcpscan.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_httpobservatory.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tlsobservatory.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_sshobservatory.json'.format(target))

        test_stepf_event = {"target": target}
        test_context = None
        results_handler = ResultsHandler(s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.generateDownloadLink(test_stepf_event, test_context)

        assert type(response) is dict
        assert response['status'] == 200
        assert type(response['output']) is dict

        url = urlparse(response['url'])
        query = parse_qs(url.query)

        assert type(query) is dict
        assert url.scheme == "https"
        assert url.netloc == "{}.s3.amazonaws.com".format(bucket_name)
        assert url.path == "/results/{}.tgz".format(target)
        assert "AWSAccessKeyId" in query
        assert "Expires" in query
        assert "Signature" in query

    def test_generateDownloadLink_partialResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # We only have some (partial) results in the S3 bucket
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_direnum.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_websearch.json'.format(target))
        client.put_object(ACL='authenticated-read', Bucket=bucket_name, Body=b'ABCD', Key='{}_tcpscan.json'.format(target))

        test_stepf_event = {"target": target}
        test_context = None
        results_handler = ResultsHandler(s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.generateDownloadLink(test_stepf_event, test_context)

        assert type(response) is dict
        assert response['status'] == 202
        assert type(response['output']) is dict

        url = urlparse(response['url'])
        query = parse_qs(url.query)

        assert type(query) is dict
        assert url.scheme == "https"
        assert url.netloc == "{}.s3.amazonaws.com".format(bucket_name)
        assert url.path == "/results/{}.tgz".format(target)
        assert "AWSAccessKeyId" in query
        assert "Expires" in query
        assert "Signature" in query

    def test_generateDownloadLink_noResults(self, s3):
        client, bucket, bucket_name = s3
        target = "infosec.mozilla.org"
        # No objects in the S3 bucket, should return no results
        test_stepf_event = {"target": target}
        test_context = None
        results_handler = ResultsHandler(client, bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.generateDownloadLink(test_stepf_event, test_context)

        assert type(response) is dict
        assert response['status'] == 404
        assert response['message'] == 'No results found for target'

    def test_generateDownloadLink_invalidEvent(self, s3):
        client, bucket, bucket_name = s3
        invalid_event = {"TEST": "TEST"}
        test_context = None
        results_handler = ResultsHandler(client, bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        response = results_handler.generateDownloadLink(invalid_event, test_context)

        assert response is False
