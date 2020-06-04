import pytest
import boto3
import botocore.client
import io
from lib.results import Results
from moto import mock_s3
from lib.target import Target

TEST_SCAN_RESULTS_BASE_PATH = '/tmp/vautomator-serverless/results'


class TestResults():
    @pytest.fixture
    def s3(self, scope="session", autouse=True):
        mock = mock_s3()
        mock.start()
        # There is currently a bug on moto, this line is needed as a workaround
        # Ref: https://github.com/spulec/moto/issues/1926
        boto3.setup_default_session()

        target = "infosec.mozilla.org"
        s3_client = boto3.client('s3', 'us-west-2')
        test_bucket_name = "test-results"
        test_bucket = s3_client.create_bucket(
            Bucket=test_bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        # Add objects to the mocked bucket
        s3_client.put_object(Bucket=test_bucket_name, Body=b'XYZ', Key='{}_httpobservatory.json'.format(target))
        s3_client.put_object(Bucket=test_bucket_name, Body=b'XYZ', Key='{}_tlsobservatory.json'.format(target))

        yield (target, s3_client, test_bucket, test_bucket_name)
        mock.stop()

    def test_defaults(self, s3):
        target, client, bucket, bucket_name = s3
        results = Results(target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        assert results.hostname == target
        assert results.base_results_path == TEST_SCAN_RESULTS_BASE_PATH
        assert type(results.bucket) is str

    def test_download(self, s3):
        target, client, bucket, bucket_name = s3
        success_result = Results(target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        success, status = success_result.download()
        assert type(success) is io.BytesIO
        assert status == 202

        new_target = "www.mozilla.org"  # An object for this host does not exist in mocked S3 bucket
        result_404 = Results(new_target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        fail_404, status = result_404.download()
        assert fail_404 is False
        assert status == 404

        bad_path = '/xyz/123'  # Such path does not exist
        result_500 = Results(target, s3_client=client, bucket=bucket_name, results_path=bad_path)
        fail_500, status = result_500.download()
        assert fail_500 is False
        assert status == 500

    def test_generateURL(self, s3):
        target, client, bucket, bucket_name = s3
        # This is the fail case, a signed URL will not be generated
        new_target = "www.mozilla.org"
        result_404 = Results(new_target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        status, output_dict, fail_404 = result_404.generateURL()
        assert status == 404
        assert fail_404 is False
        assert output_dict is False

        # Add more objects to the mocked bucket, this is the success 200 case
        client.put_object(Bucket=bucket_name, Body=b'XYZ', Key='{}_direnum.json'.format(target))
        client.put_object(Bucket=bucket_name, Body=b'XYZ', Key='{}_tcpscan.json'.format(target))
        client.put_object(Bucket=bucket_name, Body=b'XYZ', Key='{}_websearch.json'.format(target))
        client.put_object(Bucket=bucket_name, Body=b'XYZ', Key='{}_sshobservatory.json'.format(target))

        success_result = Results(target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        status, output_dict, success_200 = success_result.generateURL()
        assert type(success_200) is str
        assert status == 200
        assert True in output_dict.values()
        assert False not in output_dict.values()

        # Remove an object from the mocked bucket, this is the success 202 case
        client.delete_object(Bucket=bucket_name, Key='{}_direnum.json'.format(target))

        success_result = Results(target, s3_client=client, bucket=bucket_name, results_path=TEST_SCAN_RESULTS_BASE_PATH)
        status, output_dict, success_202 = success_result.generateURL()
        assert type(success_202) is str
        assert status == 202
        assert True in output_dict.values()
        assert False in output_dict.values()
