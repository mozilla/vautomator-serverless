import boto3
import json
import logging
import os

S3_CLIENT = boto3.client('s3')
S3_BUCKET = os.environ.get('S3_BUCKET')


def send_to_s3(hostname, scan_json, client=S3_CLIENT):
    key = "{}.{}".format(hostname, "json")

    client.put_object(Body=json.dumps(scan_json, indent=4, sort_keys=True), Bucket=S3_BUCKET,
                      Key=key, ACL='authenticated-read')
    url = "https://s3.amazonaws.com/{}/{}".format(S3_BUCKET, key)
    logging.info("Uploaded result file to URL: {}".format(url))


def search_s3(hostname, client=S3_CLIENT, bucket=S3_BUCKET):
    scan_output_list = []
    for scan_result in client.list_objects(Bucket=bucket, Prefix=hostname)['Contents']:
        scan_output_list.append(str(scan_result['Key']))

    return scan_output_list


def download_s3(scan_output, target_dir, client=S3_CLIENT, bucket=S3_BUCKET):
    if isinstance(scan_output, list):
        for output in scan_output_list:
            client.download_file(
                bucket,
                output,
                target_dir + '/{}'.format(output)
            )
    else:
        client.download_file(
            bucket,
            scan_output,
            target_dir + '/{}'.format(output)
        )
